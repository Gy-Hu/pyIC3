#!/usr/bin/env python3
"""
run_llm.py — LLM-Guided IC3 for pyIC3
=======================================

Single entry point for running IC3/PDR with LLM-generated invariant hints.

Modes:
  Single run      python run_llm.py --aag model.aag --map model.map -v source.v
  Compare         python run_llm.py --aag model.aag --map model.map -v source.v --compare
  Batch           python run_llm.py --batch
  Vanilla only    python run_llm.py --aag model.aag --no-llm
  Auto-convert    python run_llm.py -v source.v --top module_name
"""

import argparse
import os
import re
import signal
import subprocess
import time
import sys

from llm_oracle import load_llm_config, AIGERSymbolMap, PredicateEncoder

_cfg = load_llm_config()


# ── Verilog → AIGER conversion ───────────────────────────────────────

def detect_top_module(verilog_file):
    with open(verilog_file) as f:
        for line in f:
            m = re.match(r'^\s*module\s+(\w+)', line)
            if m:
                return m.group(1)
    return None


def convert_verilog(verilog_file, top_module, work_dir):
    """Verilog → aigmap → ABC optimize → fold → .aag + .map"""
    is_sv = verilog_file.endswith('.sv')
    read_cmd = "read_verilog -sv -formal" if is_sv else "read_verilog -formal"
    name = os.path.splitext(os.path.basename(verilog_file))[0]

    raw_aig  = os.path.join(work_dir, f"{name}_raw.aig")
    opt_aig  = os.path.join(work_dir, f"{name}_opt.aig")
    final_aig = os.path.join(work_dir, f"{name}.aig")
    final_aag = os.path.join(work_dir, f"{name}.aag")
    map_file  = os.path.join(work_dir, f"{name}.map")

    r = subprocess.run(["yosys", "-q", "-p", f"""
        {read_cmd} {verilog_file}; prep -top {top_module}; chformal -lower;
        flatten; memory -nordff; setundef -undriven -init -expose; setundef -anyseq;
        delete -output; techmap; aigmap;
        write_aiger -zinit -symbols -map {map_file} {raw_aig}
    """], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Yosys failed:\n{r.stderr}")

    subprocess.run(["yosys-abc", "-c",
        f"read_aiger {raw_aig}; balance; rewrite; refactor; "
        f"balance; rewrite; refactor; balance; rewrite; refactor; "
        f"write_aiger {opt_aig}"], capture_output=True)
    subprocess.run(["yosys-abc", "-c",
        f"&r {opt_aig}; &put; fold; write_aiger {final_aig}"], capture_output=True)
    subprocess.run(["aigtoaig", final_aig, final_aag], capture_output=True)

    if not os.path.exists(final_aag):
        raise RuntimeError("Conversion failed: no .aag produced")
    for f in [raw_aig, opt_aig]:
        if os.path.exists(f):
            os.remove(f)
    return final_aag, map_file


# ── IC3 runner with timeout ──────────────────────────────────────────

class _Timeout(Exception):
    pass

def _alarm_handler(signum, frame):
    raise _Timeout()

def run_ic3(aag_file, hint_lemmas=None, timeout_sec=300):
    """Returns dict with status, time, frames, sat_calls."""
    import model_encoder, pdr as pdr_mod

    m = model_encoder.Model()
    result = m.parse(aag_file)
    solver = pdr_mod.PDR(*result, silent=True)

    signal.signal(signal.SIGALRM, _alarm_handler)
    signal.alarm(timeout_sec)
    try:
        t0 = time.time()
        solver.run(hint_lemmas=hint_lemmas)
        elapsed = time.time() - t0
        signal.alarm(0)
        return dict(status="OK", time=round(elapsed, 3),
                    frames=len(solver.frames), sat_calls=solver.sum_of_sat_call)
    except _Timeout:
        signal.alarm(0)
        return dict(status="TIMEOUT", time=timeout_sec,
                    frames=len(solver.frames), sat_calls=solver.sum_of_sat_call)
    except Exception as e:
        signal.alarm(0)
        return dict(status=f"ERROR", time=0, frames=0, sat_calls=0, error=str(e))


# ── LLM hint generation ─────────────────────────────────────────────

def generate_hints(aag_file, map_file, verilog_file, api_url, api_key, model):
    """Returns (hints_list, raw_response)."""
    import model_encoder
    from llm_oracle import AIGERSymbolMap, PredicateEncoder, LLMOracle

    m = model_encoder.Model()
    result = m.parse(aag_file)
    smap = AIGERSymbolMap(map_file)
    encoder = PredicateEncoder(smap, result[1])
    verilog_src = open(verilog_file).read()

    # Auto-extract property lines from Verilog
    prop_lines = [l.strip() for l in verilog_src.split('\n')
                  if 'prop' in l.lower() and any(k in l for k in ('wire', 'assign', 'assert'))]
    prop_desc = ("Safety property:\n" + "\n".join(prop_lines)) if prop_lines else "Bad state unreachable."

    oracle = LLMOracle(api_url, api_key, model)
    return oracle.generate_hints(verilog_src, prop_desc, smap, encoder)


def fmt_time(r):
    if r['status'] == 'OK':
        return f"{r['time']:.3f}s"
    return f"T/O" if r['status'] == 'TIMEOUT' else 'ERR'


# ── Mode: single run ────────────────────────────────────────────────

def mode_single(aag, map_file, verilog, timeout, api_url, api_key, model, save_path=None):
    print(f"Generating LLM hints ({model})...")
    t0 = time.time()
    hints, raw_code = generate_hints(aag, map_file, verilog, api_url, api_key, model)
    print(f"  {len(hints)} hints in {time.time()-t0:.1f}s")

    if save_path and hints:
        from llm_oracle import save_hints
        save_hints(hints, raw_code, save_path, metadata={"model": model, "source": verilog})

    print(f"Running LLM-guided IC3 (timeout={timeout}s)...")
    r = run_ic3(aag, hint_lemmas=hints, timeout_sec=timeout)
    print(f"  {fmt_time(r)}  frames={r['frames']}  sat_calls={r['sat_calls']}")


# ── Mode: compare ───────────────────────────────────────────────────

def mode_compare(aag, map_file, verilog, timeout, api_url, api_key, model):
    print(f"Vanilla IC3 (timeout={timeout}s)...")
    r_v = run_ic3(aag, timeout_sec=timeout)
    print(f"  {fmt_time(r_v)}  frames={r_v['frames']}  sat={r_v['sat_calls']}")

    print(f"\nGenerating LLM hints ({model})...")
    try:
        hints, _ = generate_hints(aag, map_file, verilog, api_url, api_key, model)
        print(f"  {len(hints)} hints")
    except Exception as e:
        print(f"  LLM failed: {e}")
        return

    print(f"\nLLM-guided IC3 (timeout={timeout}s)...")
    r_h = run_ic3(aag, hint_lemmas=hints, timeout_sec=timeout)
    print(f"  {fmt_time(r_h)}  frames={r_h['frames']}  sat={r_h['sat_calls']}")

    if r_v['status'] == 'OK' and r_h['status'] == 'OK':
        speedup = r_v['time'] / r_h['time'] if r_h['time'] > 0 else float('inf')
        print(f"\n  Delta: frames {r_v['frames']}→{r_h['frames']}  speedup {speedup:.1f}x")


# ── Mode: batch ─────────────────────────────────────────────────────

BATCH_BENCHMARKS = {
    "client_server":        "client_server/client_server.v",
    "toy_lock_4":           "toy_lock_4/toy_lock.v",
    "h_Dekker":             "h_Dekker/main.v",
    "h_Arbiter":            "h_Arbiter/main.v",
    "h_TreeArb":            "h_TreeArb/main.sv",
    "cache_coherence_two":  "cache_coherence_two/two_processor_bin_2.v",
    "cache_coherence_three":"cache_coherence_three/three_processor_bin_2.v",
    "sw_state_machine":     "sw_state_machine/sw_state_machine.v",
    "h_Vending":            "h_Vending/main.sv",
    "Heap":                 "Heap/main.v",
    "h_CRC":                "h_CRC/main.sv",
    "h_FIFO":               "h_FIFO/main.v",
}

def mode_batch(timeout, api_url, api_key, model):
    conv_dir = "blocksys-benchmark/converted_with_map"
    orig_dir = "blocksys-benchmark/original"

    # Discover available benchmarks
    benchmarks = []
    for name, vpath in sorted(BATCH_BENCHMARKS.items()):
        aag  = os.path.join(conv_dir, f"{name}.aag")
        mapf = os.path.join(conv_dir, f"{name}.map")
        vf   = os.path.join(orig_dir, vpath)
        if os.path.exists(aag) and os.path.exists(mapf):
            benchmarks.append((name, aag, mapf, vf))
        else:
            print(f"  Skip {name}: missing .aag or .map")
    print(f"Found {len(benchmarks)} benchmarks\n")

    # Phase 1: Vanilla
    print("Phase 1: Vanilla IC3")
    print("-" * 40)
    vanilla = {}
    for name, aag, _, _ in benchmarks:
        r = run_ic3(aag, timeout_sec=timeout)
        vanilla[name] = r
        print(f"  {name:25s} {fmt_time(r):>8s}  F={r['frames']:<3d} SAT={r['sat_calls']}")

    # Phase 2: LLM hints
    print(f"\nPhase 2: Generate LLM hints ({model})")
    print("-" * 40)
    all_hints = {}
    for name, aag, mapf, vf in benchmarks:
        try:
            hints, _ = generate_hints(name, mapf, vf, api_url, api_key, model)
            # note: generate_hints takes (aag, map, verilog, ...) but benchmark
            # passes (name, map, verilog, ...) — fix below
        except Exception:
            hints = []
        # Re-call with correct signature
        try:
            hints, _ = generate_hints(aag, mapf, vf, api_url, api_key, model)
        except Exception as e:
            print(f"  {name:25s} FAILED ({e})")
            hints = []
            all_hints[name] = hints
            continue
        all_hints[name] = hints
        print(f"  {name:25s} {len(hints)} hints")

    # Phase 3: With hints
    print(f"\nPhase 3: IC3 with LLM hints")
    print("-" * 40)
    hinted = {}
    for name, aag, _, _ in benchmarks:
        hints = all_hints.get(name, [])
        r = run_ic3(aag, hint_lemmas=hints if hints else None, timeout_sec=timeout)
        hinted[name] = r
        print(f"  {name:25s} {fmt_time(r):>8s}  F={r['frames']:<3d} SAT={r['sat_calls']}")

    # Summary
    print(f"\n{'='*80}")
    print(f"  {'Benchmark':<24s} | {'Vanilla':>8s} {'F':>3s} {'SAT':>6s} | {'W/Hints':>8s} {'F':>3s} {'SAT':>6s} | {'dF':>3s} {'dTime':>9s}")
    print(f"  {'-'*24}-+-{'-'*20}-+-{'-'*20}-+-{'-'*15}")
    for name, _, _, _ in benchmarks:
        v, h = vanilla[name], hinted[name]
        vt, ht = fmt_time(v), fmt_time(h)
        if v['status'] == 'OK' and h['status'] == 'OK':
            df = h['frames'] - v['frames']
            dt = h['time'] - v['time']
            df_s = f"{df:+d}" if df != 0 else "0"
            dt_s = f"{dt:+.3f}s"
        else:
            df_s, dt_s = "-", "-"
        print(f"  {name:<24s} | {vt:>8s} {v['frames']:>3d} {v['sat_calls']:>6d} | {ht:>8s} {h['frames']:>3d} {h['sat_calls']:>6d} | {df_s:>3s} {dt_s:>9s}")
    print(f"{'='*80}")


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="LLM-Guided IC3 for pyIC3")
    p.add_argument("fileName", nargs="?",
                   help="(legacy) AIG file; equivalent to --aag <file> --no-llm")
    p.add_argument("-v", "--verilog", help="Verilog/SV source file")
    p.add_argument("-t", "--top", help="Top module (auto-detected if omitted)")
    p.add_argument("--aag", help="Pre-converted AIGER .aag file")
    p.add_argument("--map", help="AIGER .map file (from aigmap conversion)")
    p.add_argument("--compare", action="store_true", help="Run vanilla + LLM side by side")
    p.add_argument("--batch", action="store_true", help="Run all BlockSys benchmarks")
    p.add_argument("--no-llm", action="store_true", help="Vanilla IC3 only")
    p.add_argument("--load-hints", help="Load pre-verified hints from JSON (skip LLM call)")
    p.add_argument("--save-hints", help="Save generated hints to JSON for reuse")
    p.add_argument("--timeout", type=int, default=300)
    p.add_argument("--model", default=_cfg["model"])
    p.add_argument("--api-url", default=_cfg["api_url"])
    p.add_argument("--api-key", default=_cfg["api_key"])
    args = p.parse_args()

    # Legacy positional fallback: `python run.py file.aag` → vanilla IC3
    if args.fileName and not args.aag:
        args.aag = args.fileName
        args.no_llm = True

    if args.batch:
        mode_batch(args.timeout, args.api_url, args.api_key, args.model)
        return

    if not args.verilog and not args.aag:
        p.error("Need --verilog, --aag, or --batch")

    # Resolve AIGER files
    if args.aag and args.map:
        aag_file, map_file = args.aag, args.map
    elif args.verilog:
        top = args.top or detect_top_module(args.verilog)
        if not top:
            p.error("Cannot detect top module. Use --top.")
        print(f"Converting {args.verilog} (top={top})...")
        work_dir = os.path.dirname(args.verilog) or "."
        aag_file, map_file = convert_verilog(args.verilog, top, work_dir)
        with open(aag_file) as f:
            print(f"  {f.readline().strip()}")
    else:
        aag_file, map_file = args.aag, None
        args.no_llm = True

    if args.load_hints:
        # Load pre-verified hints and run IC3
        from llm_oracle import load_hints
        import model_encoder
        m_ = model_encoder.Model(); r_ = m_.parse(aag_file)
        smap_ = AIGERSymbolMap(map_file); enc_ = PredicateEncoder(smap_, r_[1])
        hints, meta = load_hints(args.load_hints, enc_)
        if meta:
            print(f"  metadata: {meta}")
        print(f"Running IC3 with {len(hints)} loaded hints (timeout={args.timeout}s)...")
        r = run_ic3(aag_file, hint_lemmas=hints, timeout_sec=args.timeout)
        print(f"  {fmt_time(r)}  frames={r['frames']}  sat_calls={r['sat_calls']}")
    elif args.no_llm:
        print(f"Running vanilla IC3 (timeout={args.timeout}s)...")
        r = run_ic3(aag_file, timeout_sec=args.timeout)
        print(f"  {fmt_time(r)}  frames={r['frames']}  sat_calls={r['sat_calls']}")
    elif args.compare:
        mode_compare(aag_file, map_file, args.verilog, args.timeout,
                     args.api_url, args.api_key, args.model)
    else:
        if not map_file or not args.verilog:
            p.error("LLM mode requires --map and --verilog (or just --verilog for auto-convert)")
        mode_single(aag_file, map_file, args.verilog, args.timeout,
                    args.api_url, args.api_key, args.model,
                    save_path=args.save_hints)


if __name__ == "__main__":
    main()
