"""
LLM-Guided IC3: Leveraging Language Models for Invariant Hint Generation
=========================================================================

Bridges the semantic gap between word-level RTL and bit-level IC3.

Pipeline (Plan A - Pre-analysis):
  1. Parse AIGER .map file → latch name-to-index mapping
  2. Call LLM with Verilog source + variable info → candidate invariants
  3. Encode invariants as Z3 clauses over AIGER latch variables
  4. Verify hints hold in initial state
  5. Inject as lemmas into IC3 frames

This is uniquely enabled by Python: LLM generates Z3 code, we eval() it.
C++/Rust IC3 implementations cannot do this.
"""

import json
import os
import requests
from z3 import *


def load_llm_config():
    """Load LLM config from .env file or environment variables."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ.setdefault(key.strip(), val.strip())
    return {
        "api_url": os.environ.get("LLM_API_URL", ""),
        "api_key": os.environ.get("LLM_API_KEY", ""),
        "model":   os.environ.get("LLM_MODEL", "claude-sonnet-4-6"),
    }


# ─────────────────────────────────────────────────────────────────────
# 1. AIGER Symbol Map Parser
# ─────────────────────────────────────────────────────────────────────

class AIGERSymbolMap:
    """Parses AIGER .map file to build Verilog name → latch index mapping."""

    def __init__(self, map_file):
        self.latch_info = {}   # latch_idx → (var_name, bit_idx, is_inverted)
        self.word_vars = {}    # var_name → [(latch_idx, bit_idx, is_inverted)]
        self.input_info = {}   # input_idx → (var_name, bit_idx)
        self._parse(map_file)

    def _parse(self, filename):
        with open(filename) as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                kind = parts[0]
                if kind in ('latch', 'invlatch'):
                    is_inv = (kind == 'invlatch')
                    idx = int(parts[1])
                    bit = int(parts[2])
                    name = parts[3]
                    self.latch_info[idx] = (name, bit, is_inv)
                    self.word_vars.setdefault(name, []).append((idx, bit, is_inv))
                elif kind == 'input':
                    idx = int(parts[1])
                    bit = int(parts[2])
                    name = parts[3]
                    self.input_info[idx] = (name, bit)

        # Regroup name[N] patterns into word-level variables.
        # e.g., "c[0]" (bit 0) and "c[1]" (bit 0) → "c" with bits 0, 1
        import re as _re
        regrouped = {}
        for name, bits in list(self.word_vars.items()):
            m = _re.match(r'^(.+)\[(\d+)\]$', name)
            if m and len(bits) == 1:
                base = m.group(1)
                bit_from_name = int(m.group(2))
                latch_idx, _, is_inv = bits[0]
                regrouped.setdefault(base, []).append((latch_idx, bit_from_name, is_inv))
            # else keep as is
        # Merge regrouped into word_vars, remove the name[N] entries
        for base, bits in regrouped.items():
            if base not in self.word_vars:
                self.word_vars[base] = bits
                # Remove individual name[N] entries
                for _, bit_idx, _ in bits:
                    old_key = f"{base}[{bit_idx}]"
                    self.word_vars.pop(old_key, None)

        # sort bits within each word variable
        for name in self.word_vars:
            self.word_vars[name].sort(key=lambda x: x[1])

    def summary(self):
        """Return human-readable summary of available variables."""
        lines = []
        for name, bits in sorted(self.word_vars.items()):
            width = len(bits)
            has_inv = any(inv for _, _, inv in bits)
            inv_note = " (some bits inverted by -zinit)" if has_inv else ""
            if width == 1:
                lines.append(f"  1-bit: {name}{inv_note}")
            else:
                lines.append(f"  {width}-bit: {name}[{width-1}:0]{inv_note}")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# 2. Predicate Encoder: word-level → bit-level Z3
# ─────────────────────────────────────────────────────────────────────

class PredicateEncoder:
    """Translates word-level Verilog predicates to Z3 over AIGER latch Bools."""

    def __init__(self, symbol_map: AIGERSymbolMap, z3_latch_vars: list):
        self.smap = symbol_map
        self.z3_vars = z3_latch_vars  # pdr.literals, indexed by latch order

    def _get_bits(self, var_name):
        """Get list of (z3_expr_for_true_value, bit_idx) for a word variable."""
        bits_info = self.smap.word_vars.get(var_name)
        if bits_info is None:
            # Progressively strip trailing [n:m] or [n] to find the base variable.
            # Handles: "pc[0][2:0]" → try "pc[0]" → found!
            #          "v.state[1:0]" → try "v.state" → found!
            import re
            candidate = var_name
            while bits_info is None:
                candidate = re.sub(r'\[\d+(?::\d+)?\]$', '', candidate)
                if candidate == var_name or not candidate:
                    break
                bits_info = self.smap.word_vars.get(candidate)
                var_name = candidate  # for next iteration
            if bits_info is None:
                raise ValueError(f"Unknown variable: {var_name}")
        result = []
        for latch_idx, bit_idx, is_inv in bits_info:
            z3_var = self.z3_vars[latch_idx]
            # If invlatch, the AIGER stores NOT(verilog_var), so true value = Not(z3_var)
            true_val = Not(z3_var) if is_inv else z3_var
            result.append((true_val, bit_idx))
        return result

    def bool_var(self, var_name):
        """Get a 1-bit Verilog variable as Z3 Bool expression."""
        # Handle "name[idx]" pattern: redirect to bit_var
        import re
        m = re.match(r'^(.+?)\[(\d+)\]$', var_name)
        if m:
            return self.bit_var(m.group(1), int(m.group(2)))
        bits = self._get_bits(var_name)
        assert len(bits) == 1, f"{var_name} is {len(bits)}-bit, not 1-bit"
        return bits[0][0]

    def word_eq_zero(self, var_name):
        """var == 0 : all bits are false."""
        return And([Not(b) for b, _ in self._get_bits(var_name)])

    def word_neq_zero(self, var_name):
        """var != 0 : at least one bit is true."""
        return Or([b for b, _ in self._get_bits(var_name)])

    def word_eq(self, var_a, var_b):
        """var_a == var_b : all corresponding bits equal."""
        bits_a = self._get_bits(var_a)
        bits_b = self._get_bits(var_b)
        assert len(bits_a) == len(bits_b), f"Width mismatch: {var_a}({len(bits_a)}) vs {var_b}({len(bits_b)})"
        return And([a == b for (a, _), (b, _) in zip(bits_a, bits_b)])

    def word_neq(self, var_a, var_b):
        """var_a != var_b."""
        return Not(self.word_eq(var_a, var_b))

    def word_lt(self, var_a, var_b):
        """Unsigned var_a < var_b, built bit-by-bit from LSB to MSB."""
        bits_a = self._get_bits(var_a)
        bits_b = self._get_bits(var_b)
        assert len(bits_a) == len(bits_b), f"Width mismatch: {var_a} vs {var_b}"
        lt = BoolVal(False)
        for (a, _), (b, _) in zip(bits_a, bits_b):  # LSB to MSB
            lt = Or(And(Not(a), b), And(a == b, lt))
        return lt

    def word_gt(self, var_a, var_b):
        """Unsigned var_a > var_b."""
        return self.word_lt(var_b, var_a)

    def word_le(self, var_a, var_b):
        """Unsigned var_a <= var_b."""
        return Not(self.word_gt(var_a, var_b))

    def word_ge(self, var_a, var_b):
        """Unsigned var_a >= var_b."""
        return Not(self.word_lt(var_a, var_b))

    def bit_var(self, var_name, bit_idx):
        """Get a specific bit of a multi-bit variable as Z3 Bool."""
        bits_info = self.smap.word_vars.get(var_name)
        if bits_info is None:
            # Same progressive stripping as _get_bits
            import re
            candidate = var_name
            while bits_info is None:
                candidate = re.sub(r'\[\d+(?::\d+)?\]$', '', candidate)
                if candidate == var_name or not candidate:
                    break
                bits_info = self.smap.word_vars.get(candidate)
                var_name = candidate
            if bits_info is None:
                raise ValueError(f"Unknown variable: {var_name}")
        for latch_idx, bidx, is_inv in bits_info:
            if bidx == bit_idx:
                z3_var = self.z3_vars[latch_idx]
                return Not(z3_var) if is_inv else z3_var
        raise ValueError(f"Bit {bit_idx} of {var_name} not found")

    def build_eval_namespace(self):
        """Build a namespace dict for eval()-ing LLM-generated Z3 code.

        The LLM writes predicates using Verilog names:
            Not(And(held_0, held_1))
            Implies(held_0, Or(ep_0_b0, ep_0_b1, ...))

        This namespace maps those names to Z3 expressions.
        """
        ns = {}
        # Z3 operators
        ns['And'] = And
        ns['Or'] = Or
        ns['Not'] = Not
        ns['Implies'] = Implies
        ns['BoolVal'] = BoolVal

        # Helper functions the LLM can call
        ns['bool_var'] = self.bool_var
        ns['bit_var'] = self.bit_var
        ns['word_eq_zero'] = self.word_eq_zero
        ns['word_neq_zero'] = self.word_neq_zero
        ns['word_eq'] = self.word_eq
        ns['word_neq'] = self.word_neq
        ns['word_lt'] = self.word_lt
        ns['word_gt'] = self.word_gt
        ns['word_le'] = self.word_le
        ns['word_ge'] = self.word_ge

        # Direct variable names for 1-bit vars
        for name, bits in self.smap.word_vars.items():
            if len(bits) == 1:
                ns[name] = self.bool_var(name)

        return ns


# ─────────────────────────────────────────────────────────────────────
# 3. LLM Oracle: calls LLM to generate invariant hints
# ─────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a formal verification expert specializing in hardware model checking.
Your task: given a Verilog module and its safety property, generate INDIVIDUALLY
INDUCTIVE invariant predicates that help an IC3/PDR model checker prove the property.

CRITICAL REQUIREMENT: Each hint must be INDIVIDUALLY relatively-inductive, meaning:
  If the hint AND the safety property both hold in some state,
  then after ONE transition step, the hint STILL holds.
  Formally: hint ∧ Post ∧ T → hint'

A simple predicate like Not(And(a, b)) is usually NOT individually inductive because
the solver cannot rule out both a and b becoming true in one step. To make it inductive,
you must COMBINE it with the conditions that prevent the violation. For example:
  - Instead of Not(And(held_0, held_1)),
    write Implies(And(held_0, held_1), word_eq("ep_0", "ep_1"))
    which is inductive because the protocol guarantees distinct epochs.
  - Or write Implies(held_0, Or(word_eq_zero("transfer_0"), ...))
    tying the state to transition guards.

Think step by step:
1. What is the key protocol mechanism that maintains safety?
2. For each invariant, WHY is it preserved by every possible transition?
3. Does each hint contain enough context to be self-sustaining?

Output ONLY a Python list named `hints`. Use these APIs:
- bool_var("name") → 1-bit Verilog variable as Z3 Bool
- bit_var("name", idx) → specific bit of multi-bit var (e.g., bit_var("nitems", 2))
- word_eq_zero("name") → multi-bit var == 0
- word_neq_zero("name") → multi-bit var != 0
- word_eq("a", "b") → two multi-bit vars are equal
- word_neq("a", "b") → two multi-bit vars differ
- word_lt("a", "b") → unsigned a < b
- word_gt("a", "b") → unsigned a > b
- word_le("a", "b") / word_ge("a", "b") → unsigned ≤ / ≥
- Z3 operators: And, Or, Not, Implies

For 1-bit variables, you can use the name directly (e.g., `held_0` instead of `bool_var("held_0")`).
IMPORTANT: use variable names exactly as shown in the symbol table. Do NOT use array slices.
Prefer STRONG composite predicates over many weak simple ones."""


def build_user_prompt(verilog_source, property_desc, symbol_summary):
    return f"""## Verilog Source
```verilog
{verilog_source}
```

## Safety Property
{property_desc}

## Available Variables (from AIGER symbol table)
{symbol_summary}

Generate candidate invariant hints. Return ONLY the Python code block with `hints = [...]`."""


class LLMOracle:
    """Calls LLM API to generate invariant hints for IC3."""

    def __init__(self, api_url, api_key, model="claude-opus-4-6"):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model

    def call_llm(self, verilog_source, property_desc, symbol_summary):
        """Call LLM and return raw response text."""
        user_msg = build_user_prompt(verilog_source, property_desc, symbol_summary)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        resp = requests.post(self.api_url, json=payload, headers=headers, timeout=180)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def generate_hints(self, verilog_source, property_desc, symbol_map, encoder):
        """Full pipeline: LLM → parse → Z3 expressions.

        Evaluates each hint individually so that a single bad reference
        (e.g., a Verilog macro name like K2) doesn't discard all hints.

        Returns:
            hints: list of Z3 Bool expressions
            raw_response: the LLM's raw text (for logging/paper)
        """
        summary = symbol_map.summary()
        raw = self.call_llm(verilog_source, property_desc, summary)

        code = _extract_code_block(raw)
        ns = encoder.build_eval_namespace()

        # Try bulk eval first (fast path)
        try:
            exec(code, ns)
            return ns.get('hints', []), raw
        except Exception:
            pass

        # Fallback: wrap each hint in try/except via rewritten code
        hints = _eval_hints_individually(code, ns)
        return hints, raw


def _eval_hints_individually(code, ns):
    """Parse the hints list from LLM code and eval each element separately."""
    import re
    # Extract the list body from "hints = [...]"
    m = re.search(r'hints\s*=\s*\[(.*)\]', code, re.DOTALL)
    if not m:
        return []

    # Split on top-level commas (not inside parentheses)
    body = m.group(1)
    elements = _split_top_level(body)

    valid = []
    for i, elem in enumerate(elements):
        elem = elem.strip()
        if not elem:
            continue
        try:
            result = eval(elem, ns)
            valid.append(result)
        except Exception as e:
            # Skip this hint, continue with others
            pass
    return valid


def _split_top_level(text):
    """Split text by commas that are not inside parentheses/brackets."""
    parts = []
    depth = 0
    current = []
    for ch in text:
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        elif ch == ',' and depth == 0:
            parts.append(''.join(current))
            current = []
            continue
        current.append(ch)
    if current:
        parts.append(''.join(current))
    return parts


def _extract_code_block(text):
    """Extract Python code from markdown code block or raw text."""
    # Try ```python ... ``` first
    import re
    m = re.search(r'```python\s*\n(.*?)```', text, re.DOTALL)
    if m:
        return m.group(1)
    # Try ``` ... ```
    m = re.search(r'```\s*\n(.*?)```', text, re.DOTALL)
    if m:
        return m.group(1)
    # Assume the whole text is code if it contains 'hints'
    if 'hints' in text:
        return text
    raise ValueError(f"Could not extract code from LLM response:\n{text[:200]}")


# ─────────────────────────────────────────────────────────────────────
# 4. Hint Injection into IC3 Frames
# ─────────────────────────────────────────────────────────────────────

def verify_and_inject(pdr_instance, hints, verbose=True):
    """Verify hints and inject into IC3 frames.

    Strategy: Tier 0 (init check) → Tier 3 (joint) → fallback Tier 2 (individual).

      Tier 0: Init ∧ ¬hint is UNSAT              (each hint holds in initial state)
      Tier 3: (∧ hints) ∧ Post ∧ T ∧ ¬(∧ hints)' is UNSAT  (jointly inductive)
      Tier 2: hint ∧ Post ∧ T ∧ ¬hint' is UNSAT  (individually relatively inductive)

    Flow:
      1. Tier 0 filters out hints that violate init.
      2. Tier 3 checks if ALL remaining hints are jointly inductive (1 SAT call).
         → Pass: inject all.
         → Fail: fallback to Tier 2, inject only individually inductive hints.

    Returns:
        number of successfully injected hints
    """
    trans = pdr_instance.trans.cube()
    post = pdr_instance.post.cube()
    primeMap = pdr_instance.primeMap
    inp_map = pdr_instance.inp_map
    init_cube = pdr_instance.init.cube()

    # ── Tier 0: filter hints that violate init ───────────────────────
    init_valid = []
    rejected_init = 0
    for i, hint in enumerate(hints):
        res = pdr_instance.check_sat(And(init_cube, Not(hint)), return_res=True)
        if res == unsat:
            init_valid.append((i, hint))
        else:
            rejected_init += 1
            if verbose:
                print(f"  [hint {i}] REJECTED (violates init): {_short_repr(hint)}")

    if not init_valid:
        if verbose:
            print(f"  → 0/{len(hints)} injected ({rejected_init} failed init)")
        return 0

    # ── Tier 3: joint inductiveness check (1 SAT call) ───────────────
    all_hints_conj = And([h for _, h in init_valid])
    all_hints_conj_prime = substitute(substitute(all_hints_conj, primeMap), inp_map)
    res3 = pdr_instance.check_sat(
        And(all_hints_conj, post, trans, Not(all_hints_conj_prime)),
        return_res=True
    )

    if res3 == unsat:
        # Tier 3 passed — all hints are jointly inductive, inject all
        for idx, hint in init_valid:
            for fidx in range(1, len(pdr_instance.frames)):
                pdr_instance.frames[fidx].addLemma(hint, pushed=False)
            if verbose:
                print(f"  [hint {idx}] INJECTED (joint): {_short_repr(hint)}")
        if verbose:
            print(f"  → {len(init_valid)}/{len(hints)} injected via Tier 3 (jointly inductive), "
                  f"{rejected_init} failed init")
        return len(init_valid)

    # ── Tier 3 failed — fallback to Tier 2: individual filtering ─────
    if verbose:
        print(f"  Tier 3 failed (not jointly inductive), falling back to Tier 2...")

    injected = 0
    rejected_ind = 0
    for idx, hint in init_valid:
        hint_prime = substitute(substitute(hint, primeMap), inp_map)
        res2 = pdr_instance.check_sat(
            And(hint, post, trans, Not(hint_prime)),
            return_res=True
        )
        if res2 == unsat:
            for fidx in range(1, len(pdr_instance.frames)):
                pdr_instance.frames[fidx].addLemma(hint, pushed=False)
            injected += 1
            if verbose:
                print(f"  [hint {idx}] INJECTED (individual): {_short_repr(hint)}")
        else:
            rejected_ind += 1
            if verbose:
                print(f"  [hint {idx}] REJECTED (not relatively inductive): {_short_repr(hint)}")

    if verbose:
        print(f"  → {injected}/{len(hints)} injected via Tier 2 fallback, "
              f"{rejected_init} failed init, {rejected_ind} failed inductiveness")
    return injected


def _short_repr(expr, max_len=80):
    """Short string repr of a Z3 expression."""
    s = str(expr)
    return s if len(s) <= max_len else s[:max_len-3] + "..."


# ─────────────────────────────────────────────────────────────────────
# 5. Hint persistence: save/load verified hints
# ─────────────────────────────────────────────────────────────────────

def save_hints(hints, raw_response, filepath, metadata=None):
    """Save verified hints to a JSON file for later reuse.

    Stores the LLM's raw response (containing the Python code block).
    On load, the code block is extracted and eval'd with the encoder.

    Args:
        hints: list of Z3 expressions (for counting)
        raw_response: the LLM's full response text
        filepath: output .json path
        metadata: optional dict (model, iterations, etc.)
    """
    import json
    code = _extract_code_block(raw_response)
    data = {
        "code": code,
        "hint_count": len(hints),
        "metadata": metadata or {},
    }
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  Saved {len(hints)} hints to {filepath}")


def load_hints(filepath, encoder):
    """Load hints from a JSON file and reconstruct Z3 expressions.

    Args:
        filepath: .json file saved by save_hints()
        encoder: PredicateEncoder instance

    Returns:
        hints: list of Z3 Bool expressions
        metadata: dict
    """
    import json
    with open(filepath) as f:
        data = json.load(f)

    ns = encoder.build_eval_namespace()
    code = data["code"]

    # Try bulk eval, fallback to per-hint
    try:
        exec(code, ns)
        hints = ns.get('hints', [])
    except Exception:
        hints = _eval_hints_individually(code, ns)

    print(f"  Loaded {len(hints)} hints from {filepath}")
    return hints, data.get("metadata", {})
