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

    def _const_bits(self, width, value):
        """Return [(BoolVal, bit_idx)] for an integer constant of given width."""
        return [(BoolVal(((value >> i) & 1) == 1), i) for i in range(width)]

    def _word_bits_or_const(self, x, ref_width=None):
        """Accept str (Verilog word name) or int (constant). Return [(bool, bit)]."""
        if isinstance(x, int):
            assert ref_width is not None, "constant needs a width reference"
            return self._const_bits(ref_width, x)
        return self._get_bits(x)

    def word_eq(self, var_a, var_b):
        """var_a == var_b. Either side may be an int constant."""
        if isinstance(var_a, int) and isinstance(var_b, int):
            return BoolVal(var_a == var_b)
        if isinstance(var_a, int):
            var_a, var_b = var_b, var_a  # canonicalize: name first
        bits_a = self._get_bits(var_a)
        bits_b = self._word_bits_or_const(var_b, ref_width=len(bits_a))
        assert len(bits_a) == len(bits_b), f"Width mismatch in word_eq({var_a},{var_b})"
        return And([a == b for (a, _), (b, _) in zip(bits_a, bits_b)])

    def word_neq(self, var_a, var_b):
        """var_a != var_b. Either side may be an int constant."""
        return Not(self.word_eq(var_a, var_b))

    def word_lt(self, var_a, var_b):
        """Unsigned var_a < var_b. Either side may be an int constant."""
        if isinstance(var_a, int) and isinstance(var_b, int):
            return BoolVal(var_a < var_b)
        # need a reference width
        ref = var_a if isinstance(var_a, str) else var_b
        ref_width = len(self._get_bits(ref))
        bits_a = self._word_bits_or_const(var_a, ref_width)
        bits_b = self._word_bits_or_const(var_b, ref_width)
        lt = BoolVal(False)
        for (a, _), (b, _) in zip(bits_a, bits_b):  # LSB to MSB
            lt = Or(And(Not(a), b), And(a == b, lt))
        return lt

    def word_gt(self, var_a, var_b):
        return self.word_lt(var_b, var_a)

    def word_le(self, var_a, var_b):
        return Not(self.word_gt(var_a, var_b))

    def word_ge(self, var_a, var_b):
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

    def idx_eq(self, idx_var, value):
        """Bool: word `idx_var` == integer constant `value` (alias for word_eq with int)."""
        return self.word_eq(idx_var, value)

    # ── Enum / state-label support ────────────────────────────────────
    def register_enum(self, field, labels):
        """Install symbolic labels for the integer values of a word field.

        e.g. register_enum("state", ["IDLE","PUSH1","PUSH2","POP1","POP2","POP3","TEST1","TEST2"])
        Then `state_in("IDLE","TEST2")` resolves to Or(idx_eq(state,0), idx_eq(state,7)).
        """
        if not hasattr(self, '_enums'):
            self._enums = {}
        self._enums[field] = {name: i for i, name in enumerate(labels)}

    def _resolve_label(self, field, label):
        if isinstance(label, int):
            return label
        enums = getattr(self, '_enums', {})
        if field in enums and label in enums[field]:
            return enums[field][label]
        raise ValueError(f"Unknown label {label!r} for field {field!r}")

    def in_set(self, field, *labels):
        """Or(idx_eq(field, v) for v in labels). Labels may be ints or registered names."""
        vals = [self._resolve_label(field, l) for l in labels]
        return Or([self.idx_eq(field, v) for v in vals])

    def state_in(self, *labels):
        """Shortcut: in_set('state', *labels)."""
        return self.in_set('state', *labels)

    def state_is(self, label):
        """Shortcut: idx_eq('state', label) — label may be int or registered name."""
        return self.idx_eq('state', self._resolve_label('state', label))

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

        ns['idx_eq']   = self.idx_eq
        ns['in_set']   = self.in_set
        ns['state_in'] = self.state_in
        ns['state_is'] = self.state_is
        ns['when']     = Implies   # alias for readability: when(cond, fact)

        # Direct variable names for 1-bit vars
        for name, bits in self.smap.word_vars.items():
            if len(bits) == 1:
                ns[name] = self.bool_var(name)

        return ns


# ─────────────────────────────────────────────────────────────────────
# 3. LLM Oracle: calls LLM to generate invariant hints
# ─────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = r"""You are a formal verification expert specializing in IC3/PDR.
Generate inductive invariant CLAUSES that help IC3 prove a safety property.

A clause is GOOD only if it is SELF-SUSTAINING — packing the predicate together
with the REASON it is preserved by the transition. A bare mutex like
`Not(And(flag_a, flag_b))` is too weak; the version that bakes in *why*
mutex holds —
    `Or(Not(flag_a), Not(flag_b), word_eq("tag_a", "tag_b"))`
— is what IC3 can propagate.

For every clause, ask: "what transition could falsify this?" and add the
condition that rules it out.

# ───────────── HINT GRAMMAR (Context-Free) ─────────────
# Output is exactly:   hints = [ Clause , Clause , ... ]
# # python comments are allowed between clauses.

Hint     ::= "hints = [" Clause ("," Clause)* "]"

Clause   ::= Atom
           | "Not(" Clause ")"
           | "And(" Clause ("," Clause)+ ")"
           | "Or("  Clause ("," Clause)+ ")"
           | "Implies(" Clause "," Clause ")"
           | "when("    Clause "," Clause ")"      # alias for Implies

Atom     ::= Bit | Word | Set | Ident

Bit      ::= "bool_var(" STR ")"            # 1-bit Verilog signal
           | "bit_var("  STR "," INT ")"    # specific bit of a multi-bit signal

Word     ::= "word_eq_zero("  STR ")"
           | "word_neq_zero(" STR ")"
           | WordCmp "(" Operand "," Operand ")"

WordCmp  ::= "word_eq" | "word_neq"
           | "word_lt" | "word_gt" | "word_le" | "word_ge"

Operand  ::= STR                            # Verilog word name (string)
           | INT                            # integer constant

Set      ::= "idx_eq("    STR "," INT  ")"          # word == const
           | "in_set("    STR "," Label ("," Label)* ")"
           | "state_in("  Label ("," Label)* ")"    # if state enum is registered
           | "state_is("  Label ")"

Label    ::= INT | STR
Ident    ::= /[a-zA-Z_]\w*/                # bare 1-bit Verilog name (auto-bound)
STR      ::= '"' /[^"]+/ '"'
INT      ::= /[0-9]+/

# ───────────── COMMON CLAUSE TEMPLATES ─────────────
# Recurring shapes across hardware/protocol benchmarks. They are SUGGESTIONS
# (not the only allowed forms). Indices i,j range over agent ids; UNROLL them
# into concrete clauses for every applicable pair — IC3 needs the full closure.

  T1  active → nonzero          Implies(active_i, word_neq_zero("val_i"))
  T2  pairwise mutex            Implies(active_i, Not(active_j))
  T3  active dominates          Implies(active_i, word_gt("val_i","val_j"))
  T4  pairwise distinct ≠0      Implies(And(word_neq_zero(a),word_neq_zero(b)),
                                        word_neq(a,b))
  T5  cached-or-null            Or(word_eq_zero("c_i"), word_eq("c_i","val_i"))
  T6  active→others quiescent   Implies(active_i, Or(word_eq_zero("pending_j"),
                                                     word_le("pending_j","mark_j")))
  T7  at-most-one-live          Implies(And(word_neq_zero("x_i"),
                                            word_gt("x_i","mark_i")),
                                        Or(word_eq_zero("x_j"),
                                           word_le("x_j","mark_j")))
  T8  state-reachability cut    when(state_in("S_A","S_B"), word_le("k", N))
  T9  counter bound             word_le("k", N)
  T10 order property            when(state_is("STABLE"),
                                     word_le("a_parent","a_child"))

These templates are not exhaustive — invent new forms when the design needs
them, as long as the result fits the grammar above.

# ───────────── DISCIPLINE ─────────────
- Output ONLY the `hints = [...]` list. No imports, no def, no assignments.
- All STR arguments must name a signal listed in the symbol summary.
- Do NOT use Verilog slice syntax `var[2:0]`; for an array element whose name
  itself contains brackets (e.g. `mem[0]`) pass the whole string to bit_var.
- Use `state_in`/`state_is` with string labels only if the symbol summary
  lists an enum mapping; otherwise pass the raw integer to `idx_eq("state", k)`.
- When the design has N replicated agents, INSTANTIATE every (i,j) pair the
  template applies to. Skipping pairs makes the conjunction non-inductive."""


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

        # Always extract just the `hints = [...]` list and eval each element
        # against our namespace. We never `exec` the LLM's preamble — it tends
        # to redefine helpers (`def bool_var(name): return Bool(name)`) which
        # silently shadow our encoder and produce uninterpreted Bools that
        # have no relation to the AIGER latches.
        hints = _eval_hints_individually(code, ns)
        return hints, raw


def _eval_hints_individually(code, ns):
    """Parse the hints list from LLM code and eval each element separately."""
    import re
    # Extract the list body from "hints = [...]"
    m = re.search(r'hints\s*=\s*\[(.*)\]', code, re.DOTALL)
    if not m:
        return []

    body = m.group(1)
    # Strip Python line comments — eval() rejects '#' inside expressions, and
    # human-written hint files (e.g. toy_lock) interleave comments with clauses.
    body = re.sub(r'#[^\n]*', '', body)
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

    # ── Pre-filter: skip non-Z3 objects (strings, None, etc.) ──────
    from z3 import is_expr
    valid_hints = [(i, h) for i, h in enumerate(hints) if is_expr(h)]
    if len(valid_hints) < len(hints) and verbose:
        print(f"  Skipped {len(hints) - len(valid_hints)} non-Z3 hints")
    hints_enum = valid_hints

    # ── Tier 0: filter hints that violate init ───────────────────────
    init_valid = []
    rejected_init = 0
    for i, hint in hints_enum:
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

    # Install any enum labels declared in metadata.enums BEFORE building the namespace.
    # e.g. {"enums": {"state": ["IDLE","PUSH1","PUSH2","POP1","POP2","POP3","TEST1","TEST2"]}}
    enums = data.get("metadata", {}).get("enums", {})
    for field, labels in enums.items():
        encoder.register_enum(field, labels)

    ns = encoder.build_eval_namespace()
    code = data["code"]

    # Always per-hint eval (see generate_hints comment).
    hints = _eval_hints_individually(code, ns)

    print(f"  Loaded {len(hints)} hints from {filepath}")
    return hints, data.get("metadata", {})
