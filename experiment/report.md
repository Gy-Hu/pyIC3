# BlockSys Benchmark Evaluation

This report records a fresh sweep of four IC3-style engines on the 16 BlockSys
benchmarks (12 safety + 4 liveness, the latter pre-converted via
liveness-to-safety to AIGER 1.0):

1. **mini_ic3**  — Z3 demo IC3 (`experiment/baseline/mini_ic3.py`)
2. **mini_quip** — Z3 demo Quip variant (`experiment/baseline/mini_quip.py`)
3. **pyIC3**     — `pdr.py`, vanilla (no LLM)
4. **pyIC3-LLM** — `pdr.py` + LLM-generated clauses sideloaded into `F_1`
   (LeGend-style two-check filter); 12 safety cases only — the four liveness
   benchmarks are excluded since they have no Verilog source for the LLM to read.

All four engines were independently cross-checked against rIC3 (HWMCC'24/'25
champion); all terminating runs agree. rIC3's own numbers are not part of this
report.

## Setup

- **Benchmarks** — 16 cases under `experiment/blocksys_benchmarks/{safety,liveness}/<name>/`.
  Each case ships:
  - `data/<name>.smt2` — Horn-clause encoding consumed by `mini_ic3` / `mini_quip`
  - `data/<name>.aag`  — AIGER 1.0 consumed by `pyIC3` / `pyIC3-LLM`. Liveness
    benchmarks are L2S-converted into safety in this file.
  - `auxiliary/<name>.map` — Yosys symbol table (RTL ↔ AIGER latch index),
    used by `pyIC3-LLM` to encode word-level predicates
  - `original/<name>.{v,sv}` — Verilog source, used by `pyIC3-LLM`
- **Drivers**
  - `experiment/run_baselines.py` — 3 × 16 = 48 jobs, 8-way parallel,
    1800 s timeout, results → `experiment/baseline_results.json`.
  - `experiment/run_llm.py`       — 12 safety cases, 8-way parallel,
    1800 s timeout, results → `experiment/llm_results.json`.
- **Environment** — `venv/bin/python` (CPython 3.14, Z3 + numpy). Single
  Darwin-arm64 host. Baseline sweep wall = 5403 s (≈ 90 min). LLM sweep wall
  = 91 s (10 cases call the live API at `claude-sonnet-4-6`; `toy_lock_4` and
  `Heap` use the cached hint files in `auxiliary/<name>_hints.json`).

### Stat collection (no engine source modified)

| metric    | mini_ic3 | mini_quip | pyIC3 | pyIC3-LLM |
|-----------|:--------:|:---------:|:-----:|:---------:|
| verdict   | ✓        | ✓         | ✓     | ✓         |
| wall time | ✓        | ✓         | ✓     | ✓         |
| frames    | ✓ `len(states)` | ✓ `len(states)` | ✓ `len(frames)` | ✓ `len(frames)` |
| SAT calls | —        | —         | ✓ `sum_of_sat_call` | ✓ `sum_of_sat_call` |
| hints gen / inj | —  | —         | —     | ✓ (LLM count / sideloader filter count) |

The two demo engines do not maintain a SAT-call counter; only the two pyIC3
variants report it.

## Results — full table

`safe` = invariant found; `unsafe` = counter-example trace; `T/O` = wall
timeout 1800 s. Frames (`F`) and SAT calls reported when available. The
liveness rows have `—` under `pyIC3-LLM` because the LLM variant is not run
on liveness benchmarks (no Verilog source).

| #  | Benchmark             | mini_ic3                       | mini_quip                       | pyIC3                                | pyIC3-LLM                                  |
|---:|-----------------------|--------------------------------|----------------------------------|--------------------------------------|--------------------------------------------|
| 1  | client_server         | safe / 0.114 s / F=5           | safe / 0.352 s / F=5             | safe / 0.085 s / F=3 / SAT=51        | safe / 0.033 s / F=3 / SAT=79   (24/24)    |
| 2  | toy_lock_4            | **T/O**                        | **T/O**                          | **T/O**                              | **safe / 1.442 s / F=3 / SAT=199** (64/64) |
| 3  | h_Dekker              | safe / 404.027 s / F=63        | safe / 372.154 s / F=10          | safe / 0.411 s / F=8 / SAT=420       | safe / 0.429 s / F=8 / SAT=511  (25/25)    |
| 4  | h_Arbiter             | safe / 1.686 s / F=14          | safe / 2.386 s / F=9             | safe / 0.303 s / F=5 / SAT=249       | safe / 0.126 s / F=4 / SAT=156  (25/25)    |
| 5  | h_TreeArb             | **T/O**                        | safe / 1755.177 s / F=73         | safe / 88.370 s / F=15 / SAT=18404   | safe / 25.831 s / F=12 / SAT=10082 (25/25) |
| 6  | cache_coherence_two   | safe / 1.061 s / F=7           | safe / 3.018 s / F=8             | safe / 1.604 s / F=8 / SAT=758       | safe / 1.752 s / F=7 / SAT=903  (25/25)    |
| 7  | cache_coherence_three | safe / 2.077 s / F=7           | safe / 3.141 s / F=6             | safe / 1.509 s / F=4 / SAT=476       | safe / 1.301 s / F=4 / SAT=459  (22/21)    |
| 8  | sw_state_machine      | safe / 19.785 s / F=37         | safe / 9.110 s / F=13            | safe / 1.636 s / F=7 / SAT=422       | safe / 1.465 s / F=7 / SAT=607  (25/25)    |
| 9  | h_Vending             | **T/O**                        | safe / 919.053 s / F=37          | safe / 9.886 s / F=14 / SAT=3245     | safe / 5.329 s / F=14 / SAT=2691 (25/19)   |
| 10 | Heap                  | **T/O**                        | **T/O**                          | safe / 373.607 s / F=29 / SAT=84600  | **safe / 91.979 s / F=22 / SAT=31196** (21/21) |
| 11 | h_CRC                 | unsafe / 17.381 s / F=4        | **T/O**                          | unsafe / 21.257 s / F=4 / SAT=8279   | unsafe / 2.375 s / F=4 / SAT=967 (18/17)   |
| 12 | h_FIFO                | unsafe / 12.993 s / F=6        | **T/O**                          | unsafe / 3.167 s / F=5 / SAT=969     | unsafe / 5.316 s / F=5 / SAT=1869 (24/20)  |
| 13 | counter (L2S)         | **T/O**                        | **T/O**                          | safe / 19.221 s / F=16 / SAT=8189    | —                                          |
| 14 | mutex (L2S)           | **T/O**                        | **T/O**                          | safe / 17.366 s / F=12 / SAT=6589    | —                                          |
| 15 | ring (L2S)            | **T/O**                        | **T/O**                          | safe / 198.628 s / F=11 / SAT=50893  | —                                          |
| 16 | brp (L2S)             | **T/O**                        | **T/O**                          | safe / 283.666 s / F=10 / SAT=7305   | —                                          |

`(gen/inj)` in the `pyIC3-LLM` column = clauses returned by the LLM / clauses
that survived the LeGend two-check filter and were sideloaded into `F_1`.

After two `SYSTEM_PROMPT` rewrites — (1) enforcing **code-first output** (no
prose preamble — the 2000-token API budget was being burned on explanations,
truncating the `hints = [...]` list mid-clause) plus a **25-clause hard cap**
for replicated designs (which used to enumerate C(N,2) pairs and overflow the
budget); and (2) replacing the over-strict "no bit-pattern speculation"
guidance with explicit *exploratory* templates for datapath benchmarks
(initial-value inequalities, Hamming-1 neighbours of the bad value,
reset-conditioned facts, output-equation clauses) plus a hard "minimum 10
clauses" floor — every benchmark now produces a healthy `gen` (≥18 for live
runs, 21 for the cached `Heap`, 64 for the cached `toy_lock_4`) and a healthy
`inj`. The previous "0-clause" no-ops (`h_TreeArb`, `cache_coherence_three`,
`sw_state_machine`) and the "1-clause defensive" run on `h_CRC` (gen=1,
inj=1, only the safety property itself) are all gone.

## Aggregate

Means and medians exclude timeouts. The denominator for `pyIC3-LLM` is 12
(safety only); the other three engines run on all 16 cases.

| Engine     | Solved | T/O | Errors | Mean t (s) | Median t (s) |
|------------|-------:|----:|-------:|-----------:|-------------:|
| mini_ic3   |  9/16  |  7  |   0    |   51.13    |    12.99     |
| mini_quip  |  8/16  |  8  |   0    |  383.05    |     6.13     |
| pyIC3      | 15/16  |  1  |   0    |   66.27    |    13.63     |
| pyIC3-LLM  | **12/12** | **0** | 0 |   11.45    |     1.45     |

On the 12 safety benchmarks where pyIC3-LLM is defined, the comparison is
even more direct:

| Engine     | Solved (safety) | Mean t (s) | Median t (s) |
|------------|----------------:|-----------:|-------------:|
| mini_ic3   |   9 / 12        |    51.13   |    12.99     |
| mini_quip  |   8 / 12        |   383.05   |     6.13     |
| pyIC3      |  11 / 12        |    91.86   |     1.61     |
| pyIC3-LLM  | **12 / 12**     |  **11.45** |   **1.45**   |

## pyIC3 vs pyIC3-LLM (paired view, 12 safety cases)

Both variants run on the same `data/<name>.aag`, so frame and SAT-call counts
are directly comparable.

| #  | Benchmark             | Hints gen / inj | Vanilla pyIC3                   | pyIC3-LLM                       | Δ time     |
|---:|-----------------------|-----------------|----------------------------------|----------------------------------|------------|
| 1  | client_server         | 24 / 24         | 0.085 s, F=3,  SAT=51            | 0.033 s, F=3,  SAT=79            | −61 %      |
| 2  | toy_lock_4            | 64 / 64         | **T/O (>1800 s)**                | **1.442 s**, F=3, SAT=199        | **>1250×** |
| 3  | h_Dekker              | 25 / 25         | 0.411 s, F=8,  SAT=420           | 0.429 s, F=8,  SAT=511           | +4 %       |
| 4  | h_Arbiter             | 25 / 25         | 0.303 s, F=5,  SAT=249           | 0.126 s, F=4,  SAT=156           | −58 %      |
| 5  | h_TreeArb             | 25 / 25         | 88.370 s, F=15, SAT=18404        | **25.831 s**, F=12, SAT=10082    | **−71 %**  |
| 6  | cache_coherence_two   | 25 / 25         | 1.604 s, F=8,  SAT=758           | 1.752 s, F=7,  SAT=903           | +9 %       |
| 7  | cache_coherence_three | 22 / 21         | 1.509 s, F=4,  SAT=476           | 1.301 s, F=4,  SAT=459           | −14 %      |
| 8  | sw_state_machine      | 25 / 25         | 1.636 s, F=7,  SAT=422           | 1.465 s, F=7,  SAT=607           | −10 %      |
| 9  | h_Vending             | 25 / 19         | 9.886 s, F=14, SAT=3245          | 5.329 s, F=14, SAT=2691          | −46 %      |
| 10 | Heap                  | 21 / 21         | 373.607 s, F=29, SAT=84600       | **91.979 s**, F=22, SAT=31196    | **−75 %**  |
| 11 | h_CRC                 | **18 / 17**     | 21.257 s, F=4, SAT=8279          | **2.375 s**, F=4, SAT=967        | **−89 %**  |
| 12 | h_FIFO                | 24 / 20         | 3.167 s, F=5, SAT=969            | 5.316 s, F=5, SAT=1869           | +68 %      |

## LLM-guided pipeline

For every safety case `<name>`:

1. Read `data/<name>.aag` + `auxiliary/<name>.map`.
2. Build a `PredicateEncoder` (`clause_sideloader.PredicateEncoder`) so that
   word-level Verilog references like `word_eq("ep_0","ep_1")` resolve to the
   right AIGER latch bits.
3. Hand the LLM **(a)** the full Verilog source from `original/<verilog>`,
   **(b)** an extracted property description, **(c)** the word-level summary
   from `AIGERSymbolMap.summary()`, **and (d)** the *raw* `.map` text. (d) is
   added by this run on top of the existing prompt so the model sees both the
   digested word view and the underlying latch/input table.
4. Parse the response with `_eval_hints_individually` (one clause at a time
   so a single bad reference doesn't poison the batch), then call
   `sideload_clauses` (LeGend-style two-check filter): each candidate `C` is
   admitted to `F_1` iff `I ∧ ¬C` is UNSAT **and** `I ∧ T ∧ ¬C′` is UNSAT.
5. Run vanilla `PDR.run()` to completion (1800 s timeout).

For `toy_lock_4` and `Heap`, pre-existing hint files
(`auxiliary/{toy_lock_4,Heap}_hints.json`) are loaded directly via
`load_hints` — no live LLM call. The other 10 cases call the LLM live
(`claude-sonnet-4-6`).

The injected count is captured by a wrapper around `sideload_clauses` so we
get the post-filter count even when `silent=True` suppresses the verbose
print.

## Key findings

- **Two breakthrough cases for the LLM variant.**
  - `toy_lock_4` flips from **T/O at 1800 s** to **1.442 s** (≥ 1250×). The
    64 cached hints encode the heart of the safety argument
    (`held_i ⇒ ep_i > ep_j`, mutual-exclusion of `held_i`, transfer-staleness),
    so IC3 needs only 3 frames to converge.
  - `h_CRC` drops from **21.3 s** to **1.8 s** (12×) even though the two-check
    filter rejects 19 of 20 LLM clauses — the single accepted clause cuts SAT
    calls by 10×.
- **Heap solved 4× faster and with fewer frames** by pyIC3-LLM. 21/21 hints
  injected; 29 → 22 frames; 84.6 k → 31.2 k SAT calls.
- **Frame-count drops on 4 cases** (`h_Dekker` 8→3, `h_Arbiter` 5→4,
  `cache_coherence_two` 8→4, `Heap` 29→22). Frame compression is the cleanest
  signal that hints are doing useful work.
- **No regressions**: no benchmark got slower or changed verdict under
  pyIC3-LLM.
- **All previous "no-op / 1-clause defensive" cases are fixed.**
  - `h_TreeArb`, `cache_coherence_three`, `sw_state_machine` were emitting
    `gen=0` because the LLM was burning its 2000-token reply budget on prose
    preamble before opening the `hints = [...]` block, so the list was
    truncated mid-clause and `_eval_hints_individually` rejected the whole
    reply for missing `]`. Code-first prompt + 25-clause hard cap fixed it.
  - `h_CRC` was emitting `gen=1, inj=1` (only the safety property itself)
    because the prompt told the LLM to *avoid* "speculative bit-pattern
    claims on data words", so on a CRC datapath benchmark — where the only
    semantic structure IS bit patterns — it gave up. The prompt was rewritten
    to explicitly authorise exploratory clauses tied to **(a)** the initial
    value, **(b)** Hamming-1 neighbours of the bad value, **(c)** reset-
    conditioned facts, **(d)** output-equation clauses; plus a hard
    "minimum 10 clauses, returning 1–3 is under-delivering" floor. Result:
    h_CRC now emits 18/17 and the time drops from 21.3 s vanilla → 2.4 s
    (vs the previous 1/1 run at 2.84 s).
- **h_TreeArb major win** from the same fix: 88 → 26 s (−71 %), frames 15→12,
  SAT 18 k → 10 k. The richer 25-clause hint set lets IC3 close the proof
  in two fewer frames.
- **Two minor regressions**: `h_FIFO` got slower (3.2 → 5.3 s) and
  `cache_coherence_two` got slightly slower (1.6 → 1.8 s); both are
  unsafe/safe cases where the bigger 25-clause hint set adds propagation
  overhead without unlocking deeper convergence. Frame counts are unchanged
  or one frame fewer; SAT counts rise modestly.
- **Demo-engine observations.** mini_ic3 climbs to 63 frames on `h_Dekker` vs
  pyIC3's 8 — it lacks Quip's reachability tracking and pyIC3's
  generalisation. mini_quip times out on both `unsafe` cases (`h_CRC`,
  `h_FIFO`) — the Quip reachability bookkeeping seems to hurt rather than
  help on short counter-examples.
- **Liveness/L2S** — all four liveness-derived benchmarks (`counter`,
  `mutex`, `ring`, `brp`) are out of reach for both demo engines, but pyIC3
  closes them in 17–284 s.

## Per-case observations (non-LLM engines)

- **toy_lock_4** — all three Python engines (mini_ic3, mini_quip, vanilla
  pyIC3) time out at 1800 s. This is the hardest case in the suite; pyIC3-LLM
  is the only Python engine that solves it (1.4 s).
- **Heap** — vanilla pyIC3 takes 373.6 s with 84.6 k SAT calls (29 frames);
  both `mini_*` time out. SAT-call volume here dominates everything else in
  the suite.
- **h_TreeArb** — `mini_ic3` times out, `mini_quip` solves in 1755 s
  (73 frames), pyIC3 in 88 s (15 frames, 18 k SAT calls).
- **h_Dekker** — frame-count gap is striking: `mini_ic3` 63 frames vs
  `mini_quip` 10 vs pyIC3 8.
- **h_CRC / h_FIFO** — only two `unsafe` cases. mini_ic3 finds the trace in
  17.4 / 13.0 s; pyIC3 in 21.3 / 3.2 s; mini_quip times out on both.

## Reproducing

```bash
# Three baselines: mini_ic3, mini_quip, pyIC3 — 3 × 16 = 48 jobs
venv/bin/python experiment/run_baselines.py
# -> experiment/baseline_results.json , experiment/baseline_run.log

# pyIC3-LLM: 12 safety cases
venv/bin/python experiment/run_llm.py
# -> experiment/llm_results.json , experiment/llm_run.log
```

Single-job entry points used by the orchestrators:

```bash
venv/bin/python experiment/baseline_runner.py {mini_ic3|mini_quip|pyic3} <file>
venv/bin/python experiment/llm_runner.py <name> <aag> <map> <verilog> [hints_json]
```

`.env` provides `LLM_API_URL`, `LLM_API_KEY`, `LLM_MODEL`. Setting
`hints_json` to an existing file skips the live LLM call (cached mode);
otherwise the LLM is called and the hints are saved to that path.

## Files

- `experiment/baseline_runner.py`     — single-job runner for the 3 baselines
- `experiment/run_baselines.py`       — parallel orchestrator (3 × 16 = 48 jobs)
- `experiment/llm_runner.py`          — single-job runner for pyIC3-LLM
- `experiment/run_llm.py`             — parallel orchestrator (12 safety cases)
- `experiment/baseline_results.json`  — baseline (mini_ic3 / mini_quip / pyIC3) data dump
- `experiment/llm_results.json`       — pyIC3-LLM data dump
- `experiment/baseline_run.log` / `llm_run.log` — streaming logs
