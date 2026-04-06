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
import requests
from z3 import *


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
            # Handle LLM patterns like "v.state[1:0]" or "name[3]"
            import re
            m = re.match(r'^(.+?)(\[[\d:]+\])+$', var_name)
            if m:
                base = m.group(1)
                bits_info = self.smap.word_vars.get(base)
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

    def bit_var(self, var_name, bit_idx):
        """Get a specific bit of a multi-bit variable as Z3 Bool."""
        bits_info = self.smap.word_vars.get(var_name)
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

        # Direct variable names for 1-bit vars
        for name, bits in self.smap.word_vars.items():
            if len(bits) == 1:
                ns[name] = self.bool_var(name)

        return ns


# ─────────────────────────────────────────────────────────────────────
# 3. LLM Oracle: calls LLM to generate invariant hints
# ─────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a formal verification expert specializing in hardware model checking.
Your task: given a Verilog module and its safety property, generate candidate
inductive invariant predicates that would help an IC3/PDR model checker prove the property.

Think about:
1. What high-level protocol invariants maintain safety?
2. What mutual exclusion / ordering constraints exist?
3. What relationships between variables are always preserved?

Output ONLY a Python list named `hints`. Use these APIs:
- bool_var("name") → 1-bit Verilog variable as Z3 Bool
- bit_var("name", idx) → specific bit of a multi-bit var (e.g., bit_var("nitems", 2))
- word_eq_zero("name") → multi-bit var == 0
- word_neq_zero("name") → multi-bit var != 0
- word_eq("a", "b") → two multi-bit vars are equal
- word_neq("a", "b") → two multi-bit vars differ
- Z3 operators: And, Or, Not, Implies

For 1-bit variables, you can use the name directly (e.g., `held_0` instead of `bool_var("held_0")`).
IMPORTANT: use variable names exactly as shown in the symbol table. Do NOT use array slices like var[2:0].

Example output:
```python
hints = [
    Not(And(held_0, held_1)),           # mutual exclusion
    Implies(held_0, word_neq_zero("ep_0")),  # epoch invariant
]
```"""


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

        Returns:
            hints: list of Z3 Bool expressions
            raw_response: the LLM's raw text (for logging/paper)
        """
        summary = symbol_map.summary()
        raw = self.call_llm(verilog_source, property_desc, summary)

        # Extract Python code block from response
        code = _extract_code_block(raw)

        # Eval in the encoder's namespace
        ns = encoder.build_eval_namespace()
        exec(code, ns)
        hints = ns.get('hints', [])

        return hints, raw


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
    """Verify hints against init state and inject into IC3 frames.

    Args:
        pdr_instance: PDR solver (after frames are initialized)
        hints: list of Z3 Bool expressions (clauses that should always hold)
        verbose: print injection status

    Returns:
        number of successfully injected hints
    """
    injected = 0
    for i, hint in enumerate(hints):
        # Check: init ∧ ¬hint is UNSAT → hint holds in initial state
        res = pdr_instance.check_sat(
            And(pdr_instance.init.cube(), Not(hint)),
            return_res=True
        )
        if res == unsat:
            # Safe to inject: add as lemma to frame 1 (and all existing frames ≥ 1)
            for fidx in range(1, len(pdr_instance.frames)):
                pdr_instance.frames[fidx].addLemma(hint, pushed=False)
            injected += 1
            if verbose:
                print(f"  [hint {i}] INJECTED: {_short_repr(hint)}")
        else:
            if verbose:
                print(f"  [hint {i}] REJECTED (violates init): {_short_repr(hint)}")

    if verbose:
        print(f"  → {injected}/{len(hints)} hints injected into IC3 frames")
    return injected


def _short_repr(expr, max_len=80):
    """Short string repr of a Z3 expression."""
    s = str(expr)
    return s if len(s) <= max_len else s[:max_len-3] + "..."
