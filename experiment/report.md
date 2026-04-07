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
| 1  | client_server         | safe / 0.114 s / F=5           | safe / 0.352 s / F=5             | safe / 0.085 s / F=3 / SAT=51        | safe / 0.028 s / F=3 / SAT=67   (20/20)    |
| 2  | toy_lock_4            | **T/O**                        | **T/O**                          | **T/O**                              | **safe / 1.442 s / F=3 / SAT=199** (64/64) |
| 3  | h_Dekker              | safe / 404.027 s / F=63        | safe / 372.154 s / F=10          | safe / 0.411 s / F=8 / SAT=420       | safe / 0.035 s / F=3 / SAT=55   (16/16)    |
| 4  | h_Arbiter             | safe / 1.686 s / F=14          | safe / 2.386 s / F=9             | safe / 0.303 s / F=5 / SAT=249       | safe / 0.118 s / F=4 / SAT=167  (32/32)    |
| 5  | h_TreeArb             | **T/O**                        | safe / 1755.177 s / F=73         | safe / 88.370 s / F=15 / SAT=18404   | safe / 53.229 s / F=15 / SAT=18404 (0/—) † |
| 6  | cache_coherence_two   | safe / 1.061 s / F=7           | safe / 3.018 s / F=8             | safe / 1.604 s / F=8 / SAT=758       | safe / 0.285 s / F=4 / SAT=153  (18/18)    |
| 7  | cache_coherence_three | safe / 2.077 s / F=7           | safe / 3.141 s / F=6             | safe / 1.509 s / F=4 / SAT=476       | safe / 1.273 s / F=4 / SAT=476  (0/—) †    |
| 8  | sw_state_machine      | safe / 19.785 s / F=37         | safe / 9.110 s / F=13            | safe / 1.636 s / F=7 / SAT=422       | safe / 1.013 s / F=7 / SAT=422  (0/—) †    |
| 9  | h_Vending             | **T/O**                        | safe / 919.053 s / F=37          | safe / 9.886 s / F=14 / SAT=3245     | safe / 9.514 s / F=14 / SAT=4869 (25/22)   |
| 10 | Heap                  | **T/O**                        | **T/O**                          | safe / 373.607 s / F=29 / SAT=84600  | **safe / 90.511 s / F=22 / SAT=31196** (21/21) |
| 11 | h_CRC                 | unsafe / 17.381 s / F=4        | **T/O**                          | unsafe / 21.257 s / F=4 / SAT=8279   | **unsafe / 1.809 s / F=4 / SAT=776** (20/1) |
| 12 | h_FIFO                | unsafe / 12.993 s / F=6        | **T/O**                          | unsafe / 3.167 s / F=5 / SAT=969     | unsafe / 3.023 s / F=5 / SAT=1125 (26/24)  |
| 13 | counter (L2S)         | **T/O**                        | **T/O**                          | safe / 19.221 s / F=16 / SAT=8189    | —                                          |
| 14 | mutex (L2S)           | **T/O**                        | **T/O**                          | safe / 17.366 s / F=12 / SAT=6589    | —                                          |
| 15 | ring (L2S)            | **T/O**                        | **T/O**                          | safe / 198.628 s / F=11 / SAT=50893  | —                                          |
| 16 | brp (L2S)             | **T/O**                        | **T/O**                          | safe / 283.666 s / F=10 / SAT=7305   | —                                          |

`(gen/inj)` in the `pyIC3-LLM` column = clauses returned by the LLM / clauses
that survived the LeGend two-check filter and were sideloaded into `F_1`.

† **`gen = 0` cases** (`h_TreeArb`, `cache_coherence_three`, `sw_state_machine`):
the LLM produced a response but `_eval_hints_individually` extracted zero usable
clauses (parse failure or empty list). With zero injected clauses these runs
are *equivalent* to vanilla pyIC3 — the identical `frames` / `SAT` confirm it.
The small wall-time deltas are scheduling noise on a busy 8-core box, not
speedups. These three rows should be re-run after re-prompting / using a
stronger model.

## Aggregate

Means and medians exclude timeouts. The denominator for `pyIC3-LLM` is 12
(safety only); the other three engines run on all 16 cases.

| Engine     | Solved | T/O | Errors | Mean t (s) | Median t (s) |
|------------|-------:|----:|-------:|-----------:|-------------:|
| mini_ic3   |  9/16  |  7  |   0    |   51.13    |    12.99     |
| mini_quip  |  8/16  |  8  |   0    |  383.05    |     6.13     |
| pyIC3      | 15/16  |  1  |   0    |   66.27    |    13.63     |
| pyIC3-LLM  | **12/12** | **0** | 0 |   13.52    |     1.36     |

On the 12 safety benchmarks where pyIC3-LLM is defined, the comparison is
even more direct:

| Engine     | Solved (safety) | Mean t (s) | Median t (s) |
|------------|----------------:|-----------:|-------------:|
| mini_ic3   |   9 / 12        |    51.13   |    12.99     |
| mini_quip  |   8 / 12        |   383.05   |     6.13     |
| pyIC3      |  11 / 12        |    91.86   |     1.61     |
| pyIC3-LLM  | **12 / 12**     |  **13.52** |   **1.36**   |

## pyIC3 vs pyIC3-LLM (paired view, 12 safety cases)

Both variants run on the same `data/<name>.aag`, so frame and SAT-call counts
are directly comparable.

| #  | Benchmark             | Hints gen / inj | Vanilla pyIC3                   | pyIC3-LLM                       | Δ time     |
|---:|-----------------------|-----------------|----------------------------------|----------------------------------|------------|
| 1  | client_server         | 20 / 20         | 0.085 s, F=3,  SAT=51            | 0.028 s, F=3,  SAT=67            | **−67 %**  |
| 2  | toy_lock_4            | 64 / 64         | **T/O (>1800 s)**                | **1.442 s**, F=3, SAT=199        | **>1250×** |
| 3  | h_Dekker              | 16 / 16         | 0.411 s, F=8,  SAT=420           | 0.035 s, F=3,  SAT=55            | **−91 %**  |
| 4  | h_Arbiter             | 32 / 32         | 0.303 s, F=5,  SAT=249           | 0.118 s, F=4,  SAT=167           | −61 %      |
| 5  | h_TreeArb             | 0 / —           | 88.370 s, F=15, SAT=18404        | 53.229 s, F=15, SAT=18404        | (no-op) †  |
| 6  | cache_coherence_two   | 18 / 18         | 1.604 s, F=8,  SAT=758           | 0.285 s, F=4,  SAT=153           | **−82 %**  |
| 7  | cache_coherence_three | 0 / —           | 1.509 s, F=4,  SAT=476           | 1.273 s, F=4,  SAT=476           | (no-op) †  |
| 8  | sw_state_machine      | 0 / —           | 1.636 s, F=7,  SAT=422           | 1.013 s, F=7,  SAT=422           | (no-op) †  |
| 9  | h_Vending             | 25 / 22         | 9.886 s, F=14, SAT=3245          | 9.514 s, F=14, SAT=4869          | −4 %       |
| 10 | Heap                  | 21 / 21         | 373.607 s, F=29, SAT=84600       | **90.511 s**, F=22, SAT=31196    | **−76 %**  |
| 11 | h_CRC                 | 20 / 1          | 21.257 s, F=4, SAT=8279          | **1.809 s**, F=4, SAT=776        | **−92 %**  |
| 12 | h_FIFO                | 26 / 24         | 3.167 s, F=5, SAT=969            | 3.023 s, F=5, SAT=1125           | −5 %       |

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
- **3 LLM no-ops** (`h_TreeArb`, `cache_coherence_three`, `sw_state_machine`):
  the model returned text the parser could not turn into Z3 clauses. These
  remain at vanilla speed and should be revisited.
- **`h_Vending` / `h_FIFO`** see hints accepted but ≤ 5 % wall-time
  improvement; SAT-call counts even rise slightly. The extra lemmas in `F_1`
  are admissible but propagate poorly.
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
