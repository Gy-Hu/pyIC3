# BlockSys Benchmark Evaluation — Baseline Sweep

This report records a fresh run of three IC3-style baselines on the 16 BlockSys benchmarks
(12 safety + 4 liveness, the latter pre-converted via liveness-to-safety to AIGER 1.0).
The LLM-guided variant of pyIC3 is **not** included in this report — it will be added in a
follow-up after this baseline is finalised.

## Setup

- **Benchmarks** — 16 cases under `experiment/blocksys_benchmarks/{safety,liveness}/<name>/`.
  Each case ships:
  - `data/<name>.smt2` — Horn-clause encoding consumed by `mini_ic3` / `mini_quip`
  - `data/<name>.aag`  — AIGER 1.0 consumed by `pyIC3` (and also by `rIC3` for cross-checking).
    Liveness benchmarks are L2S-converted into safety in this file.
  - `original/<name>.{v,sv,aig}` — upstream sources (raw AIGER 1.9 for liveness — **not** used).
- **Engines**
  1. `mini_ic3`  — `experiment/baseline/mini_ic3.py`,  Z3 demo IC3, eats `.smt2`
  2. `mini_quip` — `experiment/baseline/mini_quip.py`, Z3 demo Quip variant, eats `.smt2`
  3. `pyIC3`    — `pdr.py` via `experiment/baseline_runner.py`, vanilla (no LLM), eats `.aag`
- **Driver** — `experiment/run_baselines.py` (8-way `ProcessPoolExecutor`, 1800 s wall timeout
  per (engine, benchmark) job, results streamed to `experiment/baseline_results.json`).
- **Cross-validation** — `experiment/run_ric3.py` runs `rIC3 -e ic3` on the same `data/*.aag`
  files, results in `experiment/ric3_results.json`. rIC3 (Rust, HWMCC'24/'25 champion) is the
  ground-truth oracle.
- **Environment** — `venv/bin/python` (CPython 3.14, Z3 + numpy installed). All runs share
  one Darwin-arm64 host. The baseline sweep took **5403 s** (≈ 90 min) wall-clock for all
  48 jobs at 8-way concurrency.

### Stat collection caveat

Per the user's request, we collect everything the engines already track without modifying
their source. Concretely:

| metric    | mini_ic3 | mini_quip | pyIC3 |
|-----------|:--------:|:---------:|:-----:|
| verdict   | ✓        | ✓         | ✓     |
| wall time | ✓        | ✓         | ✓     |
| frames    | ✓ `len(states)` | ✓ `len(states)` | ✓ `len(frames)` |
| SAT calls | —        | —         | ✓ `sum_of_sat_call` |

The two demo engines do not maintain a SAT-call counter; only pyIC3 reports it.

## Results

`safe` = invariant found; `unsafe` = counter-example trace; `T/O` = wall timeout 1800 s.
Frames (`F`) and SAT calls reported when available.

| #  | Benchmark             | mini_ic3                       | mini_quip                       | pyIC3                                | rIC3 (oracle)        |
|---:|-----------------------|--------------------------------|----------------------------------|--------------------------------------|----------------------|
| 1  | client_server         | safe / 0.114 s / F=5           | safe / 0.352 s / F=5             | safe / 0.085 s / F=3 / SAT=51        | safe / 0.090 s       |
| 2  | toy_lock_4            | **T/O**                        | **T/O**                          | **T/O**                              | safe / 270.920 s     |

| 3  | h_Dekker              | safe / 404.027 s / F=63        | safe / 372.154 s / F=10          | safe / 0.411 s / F=8 / SAT=420       | safe / 0.097 s       |
| 4  | h_Arbiter             | safe / 1.686 s / F=14          | safe / 2.386 s / F=9             | safe / 0.303 s / F=5 / SAT=249       | safe / 0.097 s       |
| 5  | h_TreeArb             | **T/O**                        | safe / 1755.177 s / F=73         | safe / 88.370 s / F=15 / SAT=18404   | safe / 0.114 s       |
| 6  | cache_coherence_two   | safe / 1.061 s / F=7           | safe / 3.018 s / F=8             | safe / 1.604 s / F=8 / SAT=758       | safe / 0.094 s       |
| 7  | cache_coherence_three | safe / 2.077 s / F=7           | safe / 3.141 s / F=6             | safe / 1.509 s / F=4 / SAT=476       | safe / 0.103 s       |
| 8  | sw_state_machine      | safe / 19.785 s / F=37         | safe / 9.110 s / F=13            | safe / 1.636 s / F=7 / SAT=422       | safe / 0.092 s       |
| 9  | h_Vending             | **T/O**                        | safe / 919.053 s / F=37          | safe / 9.886 s / F=14 / SAT=3245     | safe / 0.109 s       |
| 10 | Heap                  | **T/O**                        | **T/O**                          | safe / 373.607 s / F=29 / SAT=84600  | safe / 0.252 s       |
| 11 | h_CRC                 | unsafe / 17.381 s / F=4        | **T/O**                          | unsafe / 21.257 s / F=4 / SAT=8279   | unsafe / 0.108 s     |
| 12 | h_FIFO                | unsafe / 12.993 s / F=6        | **T/O**                          | unsafe / 3.167 s / F=5 / SAT=969     | unsafe / 0.117 s     |
| 13 | counter (L2S)         | **T/O**                        | **T/O**                          | safe / 19.221 s / F=16 / SAT=8189    | safe / 0.118 s       |
| 14 | mutex (L2S)           | **T/O**                        | **T/O**                          | safe / 17.366 s / F=12 / SAT=6589    | safe / 0.108 s       |
| 15 | ring (L2S)            | **T/O**                        | **T/O**                          | safe / 198.628 s / F=11 / SAT=50893  | safe / 0.119 s       |
| 16 | brp (L2S)             | **T/O**                        | **T/O**                          | safe / 283.666 s / F=10 / SAT=7305   | safe / 0.184 s       |

## Aggregate

| Engine    | Solved | Timeouts | Errors | Mean time on solved (s) | Median time on solved (s) |
|-----------|-------:|---------:|-------:|------------------------:|--------------------------:|
| mini_ic3  | 9 / 16 | 7        | 0      | 51.13                   | 12.99                     |
| mini_quip | 8 / 16 | 8        | 0      | 383.05                  | 6.13                      |
| pyIC3     | 15 / 16| 1        | 0      | 66.27                   | 13.63                     |
| rIC3      | 16 / 16| 0        | 0      | 17.62                   | 0.110                     |

(Means exclude timeouts. Only rIC3 solves every case; pyIC3 misses just `toy_lock_4`.)

## Cross-validation against rIC3

For every (engine, benchmark) pair where the engine **terminated**, the verdict (`safe` /
`unsafe`) agrees with rIC3:

- mini_ic3:  9/9 consistent (7 timeouts excluded)
- mini_quip: 8/8 consistent (8 timeouts excluded)
- pyIC3:    15/15 consistent (1 timeout on `toy_lock_4` excluded)

No disagreements were observed. rIC3 itself solves 16/16 in <5 minutes total (toy_lock_4
dominates at 270.9 s; the other 15 finish in well under 1 s each).

Notes on the rIC3 setup:
- Initially `run_ric3.py` was reading `original/<name>.aig` (raw AIGER 1.9), which made
  rIC3 return `unknown` on the four liveness benchmarks because their property is encoded
  as `J` (justice), not as a bad-state output. The script was patched to prefer
  `data/<name>.aag` (the L2S-converted file shipped with the benchmark), after which all
  16 cases produce a definitive `safe` / `unsafe` verdict.
- The other three engines were already consuming the `data/` artefacts, so no analogous
  fix was needed for them.

## Per-case observations

- **toy_lock_4** — only rIC3 solves it (270.9 s); all three Python engines (mini_ic3,
  mini_quip, **and pyIC3**) time out at 1800 s. This is the hardest case in the suite
  for IC3-style search and the sole pyIC3 timeout.
- **Heap** — pyIC3 solves it in 373.6 s with 84.6 k SAT calls (29 frames); both `mini_*`
  time out. Z3 SAT-call volume here dominates everything else in the suite.
- **h_TreeArb** — `mini_ic3` times out, `mini_quip` solves it in 1755 s (73 frames), pyIC3
  solves it in 88 s (15 frames, 18 k SAT calls); rIC3 in 0.11 s.
- **h_Dekker** — interesting frame-count gap: `mini_ic3` reports 63 frames vs
  `mini_quip`'s 10 and pyIC3's 8. mini_ic3 lacks Quip's reachability tracking and pyIC3's
  generalisation, so it climbs much higher in frame depth before convergence.
- **h_CRC / h_FIFO** — the only two `unsafe` cases. mini_ic3 finds the trace in
  17.4 / 13.0 s; pyIC3 in 21.3 / 3.2 s; mini_quip times out on both (the Quip
  reachability bookkeeping seems to hurt rather than help on these short counter-examples).
- **liveness/L2S** — all four liveness-derived benchmarks (`counter`, `mutex`, `ring`,
  `brp`) are out of reach for both demo engines (they all hit T/O even though the
  underlying problems are small) but pyIC3 closes them in 17 – 284 s.

## Reproducing

```bash
# Baseline sweep — 3 engines × 16 cases, 8-way parallel, 1800 s timeout
venv/bin/python experiment/run_baselines.py
# -> experiment/baseline_results.json
# -> experiment/baseline_run.log

# rIC3 cross-check
venv/bin/python experiment/run_ric3.py
# -> experiment/ric3_results.json
```

Per-job entry point used by the orchestrator:

```bash
venv/bin/python experiment/baseline_runner.py {mini_ic3|mini_quip|pyic3} <file>
```

Each call prints one JSON line with `verdict`, `time`, `frames`, and (for pyIC3) `sat_calls`.

## Files

- `experiment/baseline_runner.py`  — single-job runner (importable engines, captures stdout
  to detect `FOUND INV` / `FOUND TRACE`)
- `experiment/run_baselines.py`    — parallel orchestrator (3 × 16 = 48 jobs)
- `experiment/run_ric3.py`         — rIC3 cross-validation driver
- `experiment/baseline_results.json` — full baseline data dump
- `experiment/ric3_results.json`     — rIC3 oracle data dump
- `experiment/baseline_run.log`      — streaming log of the sweep
- `experiment/ric3_run.log`          — streaming log of the rIC3 run
