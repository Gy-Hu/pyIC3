"""
Clause Sideloading for LLM-Guided IC3.

Follows the LeGend (Miao, Hu, Zhang, Zhang, 2026) sideloading discipline:
candidate clauses are injected into IC3 frame F_1 after passing two
*sanity checks*; IC3's own propagation is responsible for pushing them
forward (or letting them die).

    Reference: arxiv:2602.24010, Algorithm 3 and §3.3.2.

The two sanity checks (necessary and sufficient for soundly populating F_1):

    (1) Initiation              I ∧ ¬C is UNSAT          (C holds at init)
    (2) 1st-step consistency    I ∧ T ∧ ¬C' is UNSAT     (C holds after one step)

Together they prove C ⊇ Reach(≤1), which is exactly what F_1 must satisfy.
No relative-inductiveness check is needed at injection time — non-inductive
clauses simply fail to propagate beyond F_1 and become harmless.

Module layout:
    AIGERSymbolMap     parses Yosys aigmap .map files
    PredicateEncoder   word-level Verilog predicates → bit-level Z3
    LLMOracle          calls the LLM API to produce candidate clauses
    sideload_clauses   sanity-checks and injects clauses into F_1
    save_hints / load_hints   JSON persistence of LLM-generated clauses
"""

import json
import os
import re

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
        regrouped = {}
        for name, bits in list(self.word_vars.items()):
            m = re.match(r'^(.+)\[(\d+)\]$', name)
            if m and len(bits) == 1:
                base = m.group(1)
                bit_from_name = int(m.group(2))
                latch_idx, _, is_inv = bits[0]
                regrouped.setdefault(base, []).append((latch_idx, bit_from_name, is_inv))
        # Merge regrouped into word_vars, remove the name[N] entries
        for base, bits in regrouped.items():
            if base not in self.word_vars:
                self.word_vars[base] = bits
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

_TRAIL_INDEX_RE = re.compile(r'\[\d+(?::\d+)?\]$')


class PredicateEncoder:
    """Translates word-level Verilog predicates to Z3 over AIGER latch Bools."""

    def __init__(self, symbol_map: AIGERSymbolMap, z3_latch_vars: list):
        self.smap = symbol_map
        self.z3_vars = z3_latch_vars  # pdr.literals, indexed by latch order

    def _resolve_word(self, var_name):
        """Look up bits_info for `var_name`, progressively stripping trailing
        [n] / [n:m] indices until a known base is found.
        Returns the bits_info list, or raises ValueError if nothing matches."""
        bits_info = self.smap.word_vars.get(var_name)
        if bits_info is not None:
            return bits_info
        candidate = var_name
        while True:
            stripped = _TRAIL_INDEX_RE.sub('', candidate)
            if stripped == candidate or not stripped:
                raise ValueError(f"Unknown variable: {var_name}")
            candidate = stripped
            bits_info = self.smap.word_vars.get(candidate)
            if bits_info is not None:
                return bits_info

    def _get_bits(self, var_name):
        """Get list of (z3_expr_for_true_value, bit_idx) for a word variable."""
        bits_info = self._resolve_word(var_name)
        result = []
        for latch_idx, bit_idx, is_inv in bits_info:
            z3_var = self.z3_vars[latch_idx]
            # invlatch stores NOT(verilog_var); true value = Not(z3_var)
            true_val = Not(z3_var) if is_inv else z3_var
            result.append((true_val, bit_idx))
        return result

    def bool_var(self, var_name):
        """Get a 1-bit Verilog variable as Z3 Bool expression."""
        m = re.match(r'^(.+?)\[(\d+)\]$', var_name)
        if m:
            return self.bit_var(m.group(1), int(m.group(2)))
        bits = self._get_bits(var_name)
        assert len(bits) == 1, f"{var_name} is {len(bits)}-bit, not 1-bit"
        return bits[0][0]

    def word_eq_zero(self, var_name):
        return And([Not(b) for b, _ in self._get_bits(var_name)])

    def word_neq_zero(self, var_name):
        return Or([b for b, _ in self._get_bits(var_name)])

    def _const_bits(self, width, value):
        return [(BoolVal(((value >> i) & 1) == 1), i) for i in range(width)]

    def _word_bits_or_const(self, x, ref_width=None):
        if isinstance(x, int):
            assert ref_width is not None, "constant needs a width reference"
            return self._const_bits(ref_width, x)
        return self._get_bits(x)

    def word_eq(self, var_a, var_b):
        if isinstance(var_a, int) and isinstance(var_b, int):
            return BoolVal(var_a == var_b)
        if isinstance(var_a, int):
            var_a, var_b = var_b, var_a  # canonicalize: name first
        bits_a = self._get_bits(var_a)
        bits_b = self._word_bits_or_const(var_b, ref_width=len(bits_a))
        assert len(bits_a) == len(bits_b), f"Width mismatch in word_eq({var_a},{var_b})"
        return And([a == b for (a, _), (b, _) in zip(bits_a, bits_b)])

    def word_neq(self, var_a, var_b):
        return Not(self.word_eq(var_a, var_b))

    def word_lt(self, var_a, var_b):
        if isinstance(var_a, int) and isinstance(var_b, int):
            return BoolVal(var_a < var_b)
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
        bits_info = self._resolve_word(var_name)
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
        return self.in_set('state', *labels)

    def state_is(self, label):
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
# 3. LLM Oracle: calls LLM to generate candidate clauses
# ─────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = r"""You are a formal verification expert specializing in IC3/PDR.
Your job: emit a Python list `hints = [...]` of candidate INVARIANT CLAUSES
that help IC3 prove the given safety property.

# ═════════════════════════════════════════════════════════════════════
# OUTPUT CONTRACT — read this twice. Violating it wastes the entire reply.
# ═════════════════════════════════════════════════════════════════════
# Your reply MUST start IMMEDIATELY with a fenced Python block:
#
#     ```python
#     hints = [
#         <clause>,
#         <clause>,
#         ...
#     ]
#     ```
#
# - DO NOT write any prose, analysis, headers, or explanation BEFORE the code
#   block. Not a single sentence. Begin your response with the three backticks.
# - HARD TOKEN CAP: the API kills your reply at ~2000 tokens. If your `hints =
#   [...]` list is not CLOSED with `]` and ``` before then, the parser drops
#   ALL your work. The closing `]` is the single most important character
#   in your reply.
# - HARD CLAUSE CAP: emit AT MOST 25 clauses. After clause #25, immediately
#   write `]\n```` and stop. Even if you would "like" to enumerate more
#   pairs — DO NOT. 25 strong clauses beat 50 truncated ones.
# - NO COMMENTS inside the list. No `# ── group ──` headers, no
#   `# explanation` lines. Just raw clauses separated by commas. Comments
#   eat tokens that the closing `]` needs.
# - If you must explain, do it AFTER the closing fence; the harness ignores
#   anything outside the code block.
# - Replicated designs (N agents, N>6): do NOT enumerate every C(N,2) pair.
#   Pick a representative subset (chain pairs, neighbour pairs, or 6–10
#   carefully chosen pairs). IC3's propagation will discover the rest. The
#   risk of running out of tokens is far worse than missing a few pairs.

# ═════════════════════════════════════════════════════════════════════
# WHAT MAKES A GOOD CLAUSE
# ═════════════════════════════════════════════════════════════════════
# Each clause C is sanity-checked by two SAT queries before it is admitted:
#   (1) Initiation:        I ∧ ¬C        must be UNSAT
#   (2) 1st-step from I:   I ∧ T ∧ ¬C′   must be UNSAT
# Clauses that fail either check are silently dropped. So:
#
# - PREFER STRUCTURAL invariants over data-pattern guesses. Things that are
#   true *by construction*: mutual exclusion of one-hot state bits, "this
#   counter is bounded by N", "if controller is in state S then datapath
#   register equals X". These almost always pass both checks.
#
# - AVOID speculative bit-pattern claims on data words (e.g.
#   `bit_var("crc", 5) == 0`, "bit i and bit i+1 differ") UNLESS you can
#   point to the line in the Verilog that forces that bit. Such guesses
#   almost always fail check (1) or (2) and pollute the budget.
#
# - SELF-SUSTAINING form: bake the *reason* the predicate holds into the
#   clause body. A bare mutex like `Not(And(flag_a, flag_b))` is often too
#   weak; the strengthened version
#       `Or(Not(flag_a), Not(flag_b), word_eq("tag_a", "tag_b"))`
#   is what IC3 can propagate forward. For every clause, ask: "what
#   transition could falsify this?" and add the conjunct that rules it out.
#
# - The safety property itself (`prop` in the Verilog) is ALWAYS a legal
#   first hint. Add it.
#
# - For an N-replicated design (N agents, N caches, N processors), you MUST
#   unroll templates over EVERY (i, j) pair, not just one. Skipping pairs
#   makes the conjunction non-inductive.

# ═════════════════════════════════════════════════════════════════════
# HINT GRAMMAR (context-free, strict)
# ═════════════════════════════════════════════════════════════════════
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
           | "state_in("  Label ("," Label)* ")"    # iff state enum registered
           | "state_is("  Label ")"

Label    ::= INT | STR
Ident    ::= /[a-zA-Z_]\w*/                # bare 1-bit Verilog name (auto-bound)
STR      ::= '"' /[^"]+/ '"'
INT      ::= /[0-9]+/

# ═════════════════════════════════════════════════════════════════════
# .map / invlatch convention
# ═════════════════════════════════════════════════════════════════════
# - Symbol summary lists every Verilog name mapped to one or more AIGER latches.
# - The raw .map block uses lines `latch <idx> <bit> <name>` and
#   `invlatch <idx> <bit> <name>`. `invlatch` means the AIGER latch stores the
#   COMPLEMENT of the named bit. You do NOT need to compensate for this in
#   your clauses — the encoder already inverts the bit transparently. Just
#   reference signals by their Verilog name (`bool_var`, `word_eq`, etc.).
# - When the symbol table has both `state` and `next_state` (or any
#   `cur` / `nxt` pair), prefer the CURRENT version in your clauses; the
#   prime ′ is added automatically by the sideloader.

# ═════════════════════════════════════════════════════════════════════
# COMMON CLAUSE TEMPLATES (suggestions, not exhaustive)
# ═════════════════════════════════════════════════════════════════════
  T1  active → nonzero          Implies(active_i, word_neq_zero("val_i"))
  T2  pairwise mutex            Implies(active_i, Not(active_j))
  T3  active dominates          Implies(active_i, word_gt("val_i","val_j"))
  T4  pairwise distinct ≠0      Implies(And(word_neq_zero(a),word_neq_zero(b)),
                                        word_neq(a,b))
  T5  cached-or-null            Or(word_eq_zero("c_i"), word_eq("c_i","val_i"))
  T6  state→datapath            when(state_is("S"), word_eq("reg","const"))
  T7  bounded counter           word_le("k", N)
  T8  one-hot exclusivity       For one-hot bits b_1..b_n, emit
                                Not(And(b_i, b_j)) for every i<j pair
  T9  state-reachability cut    when(state_in("S_A","S_B"), word_le("k", N))
  T10 protocol coupling         when(is_sharedA, Or(is_sharedB, is_sharedC))
                                — directly mirrors a `prop` line from RTL

# ═════════════════════════════════════════════════════════════════════
# DISCIPLINE
# ═════════════════════════════════════════════════════════════════════
- All STR arguments must name a signal listed in the symbol summary.
- Do NOT use Verilog slice syntax `var[2:0]`; for an array element whose name
  itself contains brackets (e.g. `mem[0]`) pass the whole string to bit_var.
- Use `state_in`/`state_is` with string labels only if the symbol summary
  lists an enum mapping; otherwise pass the raw integer to `idx_eq("state", k)`.
- When the design has N replicated agents, INSTANTIATE every (i,j) pair the
  template applies to.
- The FIRST clause should be the safety property restated in this grammar.
- Stop adding clauses once you have ~30 strong ones. Brevity > exhaustion."""


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
    """Calls LLM API to generate candidate clauses for IC3 sideloading."""

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

    def generate_hints(self, verilog_source, property_desc, encoder):
        """Full pipeline: LLM → parse → Z3 expressions.

        Each clause is eval'd individually so that a single bad reference
        (e.g. a Verilog macro name like K2) doesn't discard all clauses.

        Returns:
            hints: list of Z3 Bool expressions
            raw_response: the LLM's raw text (for logging / persistence)
        """
        summary = encoder.smap.summary()
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
    m = re.search(r'hints\s*=\s*\[(.*)\]', code, re.DOTALL)
    if not m:
        return []
    body = m.group(1)
    # Strip Python line comments — eval() rejects '#' inside expressions, and
    # human-written hint files (e.g. toy_lock) interleave comments with clauses.
    body = re.sub(r'#[^\n]*', '', body)
    elements = _split_top_level(body)

    valid = []
    for elem in elements:
        elem = elem.strip()
        if not elem:
            continue
        try:
            valid.append(eval(elem, ns))
        except Exception:
            pass  # skip this clause, continue with the rest
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
    m = re.search(r'```python\s*\n(.*?)```', text, re.DOTALL)
    if m:
        return m.group(1)
    m = re.search(r'```\s*\n(.*?)```', text, re.DOTALL)
    if m:
        return m.group(1)
    if 'hints' in text:
        return text
    raise ValueError(f"Could not extract code from LLM response:\n{text[:200]}")


# ─────────────────────────────────────────────────────────────────────
# 4. Clause sideloading into IC3 frame F_1
# ─────────────────────────────────────────────────────────────────────

def sideload_clauses(pdr_instance, clauses, verbose=True):
    """LeGend-style clause sideloading.

    Each candidate clause C (a Z3 BoolExpr) is accepted iff it passes both
    of the following sanity checks:

        (1) Initiation:            I ∧ ¬C        is UNSAT
        (2) 1st-step consistency:  I ∧ T ∧ ¬C'   is UNSAT

    Accepted clauses are appended as lemmas to F_1 *only*. Non-inductive
    clauses are not filtered here — IC3's PropagateLemmas pass will quietly
    fail to push them forward, which is harmless.

    The function may be called either before pdr.run() (the standard
    pre-loaded hint flow) or mid-run from a callback: in both cases F_1
    already exists and accepting C only requires C ⊇ Reach(≤1), which the
    two checks establish.

    Args:
        pdr_instance: a pdr.PDR object whose `frames` list has been initialised
                      (i.e. `len(frames) >= 2`).
        clauses:      iterable of Z3 BoolExpr candidate clauses.
        verbose:      print per-clause accept/reject lines.

    Returns:
        Number of clauses successfully sideloaded.
    """
    assert len(pdr_instance.frames) >= 2, (
        "sideload_clauses: F_1 does not exist yet; call after pdr.frames "
        "is initialised."
    )

    init  = pdr_instance.init.cube()
    trans = pdr_instance.trans.cube()
    primeMap = pdr_instance.primeMap
    inp_map  = pdr_instance.inp_map
    frame_one = pdr_instance.frames[1]

    # Defensive: skip non-Z3 entries (None, strings, etc.)
    valid = [(i, c) for i, c in enumerate(clauses) if is_expr(c)]
    if verbose and len(valid) < len(clauses):
        print(f"  Skipped {len(clauses) - len(valid)} non-Z3 entries")

    injected = 0
    rejected_init = 0
    rejected_step = 0
    for idx, C in valid:
        # (1) Initiation: I ∧ ¬C must be UNSAT
        res_init = pdr_instance.check_sat(And(init, Not(C)), return_res=True)
        if res_init != unsat:
            rejected_init += 1
            if verbose:
                print(f"  [clause {idx}] reject (initiation): {_short_repr(C)}")
            continue

        # (2) 1st-step consistency: I ∧ T ∧ ¬C' must be UNSAT
        C_prime = substitute(substitute(C, primeMap), inp_map)
        res_step = pdr_instance.check_sat(
            And(init, trans, Not(C_prime)), return_res=True
        )
        if res_step != unsat:
            rejected_step += 1
            if verbose:
                print(f"  [clause {idx}] reject (1st-step): {_short_repr(C)}")
            continue

        # Both checks passed — sideload into F_1
        frame_one.addLemma(C, pushed=False)
        injected += 1
        if verbose:
            print(f"  [clause {idx}] sideloaded: {_short_repr(C)}")

    if verbose:
        print(
            f"  → {injected}/{len(clauses)} sideloaded "
            f"({rejected_init} failed initiation, {rejected_step} failed 1st-step)"
        )
    return injected


def _short_repr(expr, max_len=80):
    """Short string repr of a Z3 expression."""
    s = str(expr)
    return s if len(s) <= max_len else s[:max_len - 3] + "..."


# ─────────────────────────────────────────────────────────────────────
# 5. Hint persistence: save/load verified clauses
# ─────────────────────────────────────────────────────────────────────

def save_hints(hints, raw_response, filepath, metadata=None):
    """Save verified hints to a JSON file for later reuse.

    Stores the LLM's raw response (containing the Python code block).
    On load, the code block is extracted and eval'd with the encoder.

    Args:
        hints: list of Z3 expressions (for counting only)
        raw_response: the LLM's full response text
        filepath: output .json path
        metadata: optional dict (model, source, enums, ...)
    """
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
    with open(filepath) as f:
        data = json.load(f)

    # Install any enum labels declared in metadata.enums BEFORE building the namespace.
    # e.g. {"enums": {"state": ["IDLE","PUSH1","PUSH2","POP1","POP2","POP3","TEST1","TEST2"]}}
    enums = data.get("metadata", {}).get("enums", {})
    for field, labels in enums.items():
        encoder.register_enum(field, labels)

    ns = encoder.build_eval_namespace()
    code = data["code"]
    hints = _eval_hints_individually(code, ns)

    print(f"  Loaded {len(hints)} hints from {filepath}")
    return hints, data.get("metadata", {})
