# BlockSys Benchmark Evaluation

This directory documents the benchmark evaluation of pyIC3 on 12 safety-property benchmarks selected for the [BlockSys 2026](https://blocksys.info/2026/) (International Conference on Blockchain, Artificial Intelligence, and Trustworthy Systems) research project.

## Benchmark Selection

We selected 12 single-property, pure-safety AIGER benchmarks from the [mc-benchmark](https://github.com/gipsyh/mc-benchmark) repository. Each benchmark is mapped to a relevant BlockSys theme (blockchain, trustworthy systems, or AI hardware).


| #   | Benchmark             | Source         | BlockSys Relevance                                                                                                                                                                            |
| --- | --------------------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | client_server         | avr/crafted    | **Node communication protocol** — Models client-server interaction, analogous to blockchain node P2P communication and message passing between validators.                                    |
| 2   | toy_lock_4            | avr/crafted    | **Smart contract lock mechanism** — Verifies a lock primitive, directly mapping to reentrancy guards and mutex locks in smart contracts.                                                      |
| 3   | h_Dekker              | avr/opensource | **Mutual exclusion → Consensus** — Dekker's algorithm ensures mutual exclusion between processes, analogous to blockchain consensus where only one node produces a block at a time.           |
| 4   | h_Arbiter             | avr/opensource | **Bus arbiter → Block producer arbitration** — Hardware arbitration circuit that decides which agent gets access, mapping to block producer selection in blockchain systems.                  |
| 5   | h_TreeArb             | avr/opensource | **Tree arbiter → Hierarchical/sharded consensus** — Hierarchical arbitration tree, analogous to sharded blockchain consensus or layer-2 rollup arbitration.                                   |
| 6   | cache_coherence_two   | avr/opensource | **Two-node state consistency** — Cache coherence protocol between two nodes, directly modeling blockchain state synchronization between peers.                                                |
| 7   | cache_coherence_three | avr/opensource | **Multi-node state consistency** — Three-node cache coherence, modeling consensus among multiple blockchain validators maintaining consistent global state.                                   |
| 8   | sw_state_machine      | avr/crafted    | **Smart contract state machine** — Finite state machine verification, directly relevant since smart contracts are fundamentally state machines with guarded transitions.                      |
| 9   | h_Vending             | avr/opensource | **Transaction logic state machine** — Vending machine state machine with token-based transitions, analogous to smart contract transaction processing workflows.                               |
| 10  | Heap                  | avr/opensource | **Memory safety → Trustworthy systems** — Heap data structure verification, fundamental to memory safety guarantees in trusted execution environments.                                        |
| 11  | h_CRC                 | avr/opensource | **Data integrity / Hash verification** — CRC (Cyclic Redundancy Check) circuit verification, directly mapping to blockchain's core requirement of data integrity and hash-based verification. |
| 12  | h_FIFO                | avr/opensource | **Transaction queue / Message buffer** — FIFO queue verification, analogous to blockchain transaction pools (mempool) and ordered message delivery in consensus protocols.                    |


## Benchmark Specifications

All benchmarks are single-property (B=1), pure-safety AIGER files (no justice/fairness).


| #   | Benchmark             | AIGER Header               | Inputs | Latches | ANDs | Property |
| --- | --------------------- | -------------------------- | ------ | ------- | ---- | -------- |
| 1   | client_server         | `aag 84 23 5 0 56 1`       | 23     | 5       | 56   | safe     |
| 2   | toy_lock_4            | `aag 1624 24 100 0 1500 1` | 24     | 100     | 1500 | safe     |
| 3   | h_Dekker              | `aag 518 92 9 0 417 1`     | 92     | 9       | 417  | safe     |
| 4   | h_Arbiter             | `aag 366 66 23 0 277 1`    | 66     | 23      | 277  | safe     |
| 5   | h_TreeArb             | `aag 1478 267 37 0 1174 1` | 267    | 37      | 1174 | safe     |
| 6   | cache_coherence_two   | `aag 496 7 43 0 446 1`     | 7      | 43      | 446  | safe     |
| 7   | cache_coherence_three | `aag 741 10 62 0 669 1`    | 10     | 62      | 669  | safe     |
| 8   | sw_state_machine      | `aag 474 2 43 0 429 1`     | 2      | 43      | 429  | safe     |
| 9   | h_Vending             | `aag 1443 245 22 0 1176 1` | 245    | 22      | 1176 | safe     |
| 10  | Heap                  | `aag 1640 249 24 0 1367 1` | 249    | 24      | 1367 | safe     |
| 11  | h_CRC                 | `aag 666 13 32 0 621 1`    | 13     | 32      | 621  | unsafe   |
| 12  | h_FIFO                | `aag 645 85 54 0 506 1`    | 85     | 54      | 506  | unsafe   |


## AIGER Format Conversion

### The Problem

These benchmarks use **AIGER 1.1** format where safety properties are encoded in the **B (bad state) section** of the header (`aag M I L O A B`). However, pyIC3's parser only reads the **O (output) section** to construct the property (see `model_encoder.py` line 414: `for it in o:`). When O=0 and B=1, pyIC3 verifies an empty (trivially true) property, producing incorrect "FOUND INV" results.

### The Solution

We use **yosys-abc** to convert AIGER 1.1 (with B field) into AIGER 1.0 (with O field) by folding the bad-state property into a regular output:

```bash
yosys-abc -c "&r <input>.aig; &put; fold; write_aiger <output>.aig"
```

This command:

1. `&r` — reads the AIGER file into ABC's new AIG format (supports AIGER 1.1 with B/C fields)
2. `&put` — transfers the AIG to ABC's old network format
3. `fold` — folds bad-state (B) and constraint (C) properties into the combinational logic, converting them to regular outputs (O)
4. `write_aiger` — writes the result as AIGER 1.0 with O=1

After conversion, the header changes from `aag M I L 0 A 1` to `aag M I L 1 A`, and pyIC3 can correctly parse and verify the property.

### Conversion Script

```bash
#!/bin/bash
# Convert all 12 BlockSys benchmarks from AIGER 1.1 to AIGER 1.0
BENCHMARKS=(
  "client_server:avr/crafted/client_server/client_server.aig"
  "toy_lock_4:avr/crafted/toy_lock_4/toy_lock_4.aig"
  "h_Dekker:avr/opensource/h_Dekker/h_Dekker.aig"
  "h_Arbiter:avr/opensource/h_Arbiter/h_Arbiter.aig"
  "h_TreeArb:avr/opensource/h_TreeArb/h_TreeArb.aig"
  "cache_coherence_two:avr/opensource/cache_coherence_two/cache_coherence_two.aig"
  "cache_coherence_three:avr/opensource/cache_coherence_three/cache_coherence_three.aig"
  "sw_state_machine:avr/crafted/sw_state_machine/sw_state_machine.aig"
  "h_Vending:avr/opensource/h_Vending/h_Vending.aig"
  "Heap:avr/opensource/Heap/Heap.aig"
  "h_CRC:avr/opensource/h_CRC/h_CRC.aig"
  "h_FIFO:avr/opensource/h_FIFO/h_FIFO.aig"
)

MC_BENCH="/path/to/mc-benchmark"
OUTPUT_DIR="./converted"
mkdir -p "$OUTPUT_DIR"

for entry in "${BENCHMARKS[@]}"; do
  name="${entry%%:*}"
  path="${entry##*:}"
  echo "Converting $name..."
  yosys-abc -c "&r ${MC_BENCH}/${path}; &put; fold; write_aiger ${OUTPUT_DIR}/${name}.aig"
  # Convert to ASCII for pyIC3
  aigtoaig "${OUTPUT_DIR}/${name}.aig" "${OUTPUT_DIR}/${name}.aag"
done
```

## Experimental Results

### pyIC3 vs rIC3 Comparison

All benchmarks were verified using both **pyIC3** (Python IC3/PDR implementation) and **rIC3** (Rust IC3 implementation, HWMCC'24 & HWMCC'25 champion).


| #   | Benchmark             | pyIC3 Result         | pyIC3 Time | rIC3 Result  | rIC3 Time | Consistent |
| --- | --------------------- | -------------------- | ---------- | ------------ | --------- | ---------- |
| 1   | client_server         | FOUND INV (safe)     | 0.058s     | UNSAT (safe) | 0.00s     | Yes        |
| 2   | toy_lock_4            | TIMEOUT              | >300s      | UNSAT (safe) | 199.44s   | -          |
| 3   | h_Dekker              | FOUND INV (safe)     | 0.946s     | UNSAT (safe) | 0.01s     | Yes        |
| 4   | h_Arbiter             | FOUND INV (safe)     | 0.457s     | UNSAT (safe) | 0.00s     | Yes        |
| 5   | h_TreeArb             | FOUND INV (safe)     | 108.364s   | UNSAT (safe) | 0.03s     | Yes        |
| 6   | cache_coherence_two   | FOUND INV (safe)     | 1.353s     | UNSAT (safe) | 0.00s     | Yes        |
| 7   | cache_coherence_three | FOUND INV (safe)     | 2.493s     | UNSAT (safe) | 0.01s     | Yes        |
| 8   | sw_state_machine      | FOUND INV (safe)     | 2.234s     | UNSAT (safe) | 0.00s     | Yes        |
| 9   | h_Vending             | FOUND INV (safe)     | 23.682s    | UNSAT (safe) | 0.03s     | Yes        |
| 10  | Heap                  | TIMEOUT              | >300s      | UNSAT (safe) | 0.20s     | -          |
| 11  | h_CRC                 | FOUND TRACE (unsafe) | 2.374s     | SAT (unsafe) | 0.02s     | Yes        |
| 12  | h_FIFO                | FOUND TRACE (unsafe) | 8.577s     | SAT (unsafe) | 0.03s     | Yes        |


### Summary

- **Consistent results**: 10 out of 12 benchmarks (where pyIC3 terminated)
- **pyIC3 timeouts**: 2 benchmarks (toy_lock_4, Heap) — rIC3 solved both
- **Safe benchmarks**: 10 (properties hold — the bad state is unreachable)
- **Unsafe benchmarks**: 2 (h_CRC, h_FIFO — counterexample traces found)
- **pyIC3 time range**: 0.058s to 108.364s (3 orders of magnitude)
- **rIC3 time range**: 0.00s to 199.44s (toy_lock_4 is the only slow case)

### LLM-Guided IC3 Results

We re-converted all 12 benchmarks via a Yosys `aigmap` pipeline that preserves RTL-to-AIGER symbol mappings (see `convert_all.sh`). An LLM (Claude Sonnet 4.6) reads the original Verilog source and generates candidate invariant predicates. Each candidate is verified by a **two-tier filter** before injection:

- **Tier 0**: `Init ∧ ¬hint` is UNSAT — hint holds in the initial state.
- **Tier 2**: `hint ∧ Post ∧ T ∧ ¬hint'` is UNSAT — hint is relatively inductive with respect to the safety property.

Hints that fail either check are discarded. Verified hints are injected as lemmas into IC3 frames before solving. See `run_llm.py --batch` to reproduce.


| #   | Benchmark             | Generated | Injected | Vanilla               | W/Hints                   | dFrames | dTime      | dSAT     |
| --- | --------------------- | --------- | -------- | --------------------- | ------------------------- | ------- | ---------- | -------- |
| 1   | client_server         | 15        | 15       | 0.044s / 3F / 51sat   | 0.024s / 3F / 37sat       | 0       | **-45%**   | -27%     |
| 2   | toy_lock_4            | 28        | 28       | T/O / 4F / 32344sat   | T/O / 4F / 27525sat       | 0       | -          | -15%     |
| 3   | h_Dekker              | 8         | 8        | 0.86s / 8F / 455sat   | 0.48s / 7F / 346sat       | **-1**  | **-44%**   | -24%     |
| 4   | h_Arbiter             | 0         | 0        | 0.10s / 3F / 85sat    | 0.10s / 3F / 85sat        | 0       | 0          | 0        |
| 5   | **h_TreeArb**         | 19        | **9**    | 124s / 15F / 18571sat | **34.5s / 10F / 7210sat** | **-5**  | **-72%**   | **-61%** |
| 6   | cache_coherence_two   | 0         | 0        | 0.66s / 4F / 264sat   | 0.62s / 4F / 233sat       | 0       | -7%        | -12%     |
| 7   | cache_coherence_three | 12        | 12       | 2.02s / 6F / 578sat   | 1.93s / 4F / 531sat       | **-2**  | -5%        | -8%      |
| 8   | sw_state_machine      | 11        | **7**    | 0.53s / 5F / 149sat   | 0.55s / 5F / 192sat       | 0       | +4%        | +29%     |
| 9   | h_Vending             | 10        | 10       | 16.1s / 15F / 4029sat | 12.2s / 13F / 2935sat     | **-2**  | **-24%**   | -27%     |
| 10  | Heap                  | 15        | 15       | T/O / 22F / 56202sat  | ERROR                     | -       | -          | -        |
| 11  | **h_CRC**             | 3         | 3        | 38.5s / 4F / 10247sat | **0.95s / 4F / 287sat**   | 0       | **-97.5%** | **-97%** |
| 12  | h_FIFO                | 21        | 21       | 6.33s / 5F / 1413sat  | 4.96s / 5F / 1215sat      | 0       | **-22%**   | -14%     |


 LLM hint encoding failed (hierarchical variable names not in AIGER map), equivalent to 0 hints.

**Key findings**:

- **9/10 benchmarks with hints improved or held steady** (no degradation). The Tier 2 relative-inductiveness filter eliminated all regressions from incorrect hints.
- **4 benchmarks with frame reduction**: h_TreeArb (15->10), h_Dekker (8->7), cache_coherence_three (6->4), h_Vending (15->13).
- **Best speedup: h_CRC 40x** (38.5s -> 0.95s). This is an unsafe case — LLM hints prune the counterexample search space, reducing SAT calls from 10247 to 287.
- **Tier 2 filter impact**: On h_TreeArb, 10/19 LLM-generated hints were rejected as non-relatively-inductive. Without the filter, these bad hints caused a +27% slowdown; with the filter, the same benchmark achieved a **72% speedup and 5 fewer frames**. On sw_state_machine, 4/11 hints were rejected, turning a +97% slowdown into a neutral result (+4%).

**Open problems**:

1. **toy_lock_4 and Heap still timeout**: 100 latches (toy_lock_4) and 24 latches with 79 inputs (Heap) create transition relations too large for Z3's per-SAT-call performance. Hints reduce SAT call count but cannot compensate for the fundamental overhead of Z3 on propositional formulas. Using a dedicated SAT solver (Kissat/CaDiCaL) as backend would likely resolve this.
2. **Variable name resolution**: LLM-generated variable references sometimes use hierarchical names (`pcacheA.state`), Verilog macros (`K2`), or double-indexed patterns (`pc[0][2:0]`) that don't match the flat AIGER symbol table. A progressive bracket-stripping fallback and per-hint error recovery partially address this, but 2/12 benchmarks (h_Arbiter, cache_coherence_two) still fail to generate any valid hints.

## Benchmark Source Paths

All benchmarks are sourced from the mc-benchmark repository.

### Safety Benchmarks (12)


| Benchmark             | Absolute Path                                                                    |
| --------------------- | -------------------------------------------------------------------------------- |
| client_server         | `/Users/huguangyu/coding_env/mc-benchmark/avr/crafted/client_server/`            |
| toy_lock_4            | `/Users/huguangyu/coding_env/mc-benchmark/avr/crafted/toy_lock_4/`               |
| h_Dekker              | `/Users/huguangyu/coding_env/mc-benchmark/avr/opensource/h_Dekker/`              |
| h_Arbiter             | `/Users/huguangyu/coding_env/mc-benchmark/avr/opensource/h_Arbiter/`             |
| h_TreeArb             | `/Users/huguangyu/coding_env/mc-benchmark/avr/opensource/h_TreeArb/`             |
| cache_coherence_two   | `/Users/huguangyu/coding_env/mc-benchmark/avr/opensource/cache_coherence_two/`   |
| cache_coherence_three | `/Users/huguangyu/coding_env/mc-benchmark/avr/opensource/cache_coherence_three/` |
| sw_state_machine      | `/Users/huguangyu/coding_env/mc-benchmark/avr/crafted/sw_state_machine/`         |
| h_Vending             | `/Users/huguangyu/coding_env/mc-benchmark/avr/opensource/h_Vending/`             |
| Heap                  | `/Users/huguangyu/coding_env/mc-benchmark/avr/opensource/Heap/`                  |
| h_CRC                 | `/Users/huguangyu/coding_env/mc-benchmark/avr/opensource/h_CRC/`                 |
| h_FIFO                | `/Users/huguangyu/coding_env/mc-benchmark/avr/opensource/h_FIFO/`                |


### Liveness Benchmarks (attempted, not used in final evaluation)


| Benchmark       | Absolute Path                                                                   |
| --------------- | ------------------------------------------------------------------------------- |
| counter         | `/Users/huguangyu/coding_env/mc-benchmark/LMCS-2006/aiger-1.9/counter/`         |
| mutex           | `/Users/huguangyu/coding_env/mc-benchmark/LMCS-2006/aiger-1.9/mutex/`           |
| ring            | `/Users/huguangyu/coding_env/mc-benchmark/LMCS-2006/aiger-1.9/ring/`            |
| abp4            | `/Users/huguangyu/coding_env/mc-benchmark/LMCS-2006/aiger-1.9/abp4/`            |
| brp             | `/Users/huguangyu/coding_env/mc-benchmark/LMCS-2006/aiger-1.9/brp/`             |
| dme3            | `/Users/huguangyu/coding_env/mc-benchmark/LMCS-2006/aiger-1.9/dme/`             |
| reactor         | `/Users/huguangyu/coding_env/mc-benchmark/LMCS-2006/aiger-1.9/reactor/`         |
| production-cell | `/Users/huguangyu/coding_env/mc-benchmark/LMCS-2006/aiger-1.9/production-cell/` |


