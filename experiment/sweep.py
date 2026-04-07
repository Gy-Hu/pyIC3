#!/usr/bin/env python3
"""Unified experiment driver for the BlockSys benchmarks.

Subcommands
-----------
  baseline   Run the 3 Python baselines (mini_ic3, mini_quip, pyIC3) on
             all 16 cases. Streams to experiment/baseline_results.json.
  llm        Run pyIC3-LLM on the 12 safety cases. Streams to
             experiment/llm_results.json.
  ric3       Run rIC3 -e ic3 on the 16 cases (oracle cross-check).
             Streams to experiment/ric3_results.json.
  worker     Single-job mode. Used internally by the orchestrators via
             subprocess; emits one JSON line on stdout. Also exposed as
             a CLI for ad-hoc debugging.

The "runner" and "orchestrator" roles all live in this one file. The
orchestrators invoke `python sweep.py worker ...` as subprocesses so each
job gets a fresh interpreter and a hard wall timeout.

Examples
--------
  python experiment/sweep.py baseline
  python experiment/sweep.py llm
  python experiment/sweep.py ric3
  python experiment/sweep.py worker baseline pyic3 path/to/file.aag
  python experiment/sweep.py worker llm h_CRC <aag> <map> <verilog> [hints.json]
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import io
import json
import os
import re
import subprocess
import sys
import time
import traceback
from contextlib import redirect_stdout, redirect_stderr

# ── paths ────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, "venv", "bin", "python")
SCRIPT = os.path.join(ROOT, "experiment", "sweep.py")
BENCH_ROOT = os.path.join(ROOT, "experiment", "blocksys_benchmarks")
SAFETY = os.path.join(BENCH_ROOT, "safety")

TIMEOUT = 1800
WORKERS = 8

sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "experiment", "baseline"))


# ── benchmark inventory ──────────────────────────────────────────────
def collect_all_benchmarks():
    """All 16 cases (12 safety + 4 liveness). Returns list of
    (category, name, smt2, aag)."""
    cases = []
    for sub in ("safety", "liveness"):
        for d in sorted(glob.glob(os.path.join(BENCH_ROOT, sub, "*"))):
            name = os.path.basename(d)
            cases.append((
                sub, name,
                os.path.join(d, "data", f"{name}.smt2"),
                os.path.join(d, "data", f"{name}.aag"),
            ))
    return cases


# (name → verilog basename) for the 12 safety cases that have RTL source
SAFETY_VERILOG = {
    "client_server":         "client_server.v",
    "toy_lock_4":            "toy_lock.v",
    "h_Dekker":              "main.v",
    "h_Arbiter":             "main.v",
    "h_TreeArb":             "main.sv",
    "cache_coherence_two":   "two_processor_bin_2.v",
    "cache_coherence_three": "three_processor_bin_2.v",
    "sw_state_machine":      "sw_state_machine.v",
    "h_Vending":             "main.sv",
    "Heap":                  "main.v",
    "h_CRC":                 "main.sv",
    "h_FIFO":                "main.v",
}


def collect_safety_with_verilog():
    """The 12 safety cases as (name, aag, map, verilog, hints_json) tuples."""
    out = []
    for name in sorted(SAFETY_VERILOG):
        d = os.path.join(SAFETY, name)
        aag = os.path.join(d, "data",      f"{name}.aag")
        mapf = os.path.join(d, "auxiliary", f"{name}.map")
        v = os.path.join(d, "original",  SAFETY_VERILOG[name])
        hints = os.path.join(d, "auxiliary", f"{name}_hints.json")
        if all(os.path.exists(p) for p in (aag, mapf, v)):
            out.append((name, aag, mapf, v, hints))
        else:
            print(f"  skip {name}: missing input file")
    return out


# ── worker: baseline (mini_ic3 / mini_quip / pyic3) ──────────────────
def _verdict_from_stdout(s):
    if "FOUND INV" in s or "Invariant:" in s:
        return "safe"
    if "FOUND TRACE" in s or "Trace" in s:
        return "unsafe"
    return "unknown"


def _baseline_mini_ic3(path):
    import mini_ic3 as m
    h = m.Horn2Transitions(); h.parse(path)
    solver = m.MiniIC3(h.init, h.trans, h.goal, h.xs, h.inputs, h.xns)
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        r = solver.run()
    from z3 import ExprRef
    if isinstance(r, m.Goal):
        verdict = "unsafe"
    elif isinstance(r, ExprRef):
        verdict = "safe"
    else:
        verdict = _verdict_from_stdout(buf.getvalue())
    return verdict, dict(frames=len(getattr(solver, "states", [])))


def _baseline_mini_quip(path):
    import mini_quip as m
    h = m.Horn2Transitions(); h.parse(path)
    solver = m.Quip(h.init, h.trans, h.goal, h.xs, h.inputs, h.xns)
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        r = solver.run()
    from z3 import ExprRef
    if isinstance(r, m.QGoal):
        verdict = "unsafe"
    elif isinstance(r, ExprRef):
        verdict = "safe"
    else:
        verdict = _verdict_from_stdout(buf.getvalue())
    return verdict, dict(frames=len(getattr(solver, "states", [])),
                         count_may=getattr(solver, "count_may", None))


def _baseline_pyic3(path):
    import model_encoder, pdr as pdr_mod
    mdl = model_encoder.Model()
    res = mdl.parse(path)
    solver = pdr_mod.PDR(*res, silent=True)
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        solver.run()
    return _verdict_from_stdout(buf.getvalue()), dict(
        frames=len(solver.frames),
        sat_calls=getattr(solver, "sum_of_sat_call", None),
    )


BASELINE_ENGINES = {
    "mini_ic3":  _baseline_mini_ic3,
    "mini_quip": _baseline_mini_quip,
    "pyic3":     _baseline_pyic3,
}


def worker_baseline(engine, path):
    fn = BASELINE_ENGINES[engine]
    t0 = time.time()
    try:
        verdict, stats = fn(path)
        out = dict(engine=engine, file=path, status="ok", verdict=verdict,
                   time=round(time.time() - t0, 3), **stats)
    except Exception as e:
        out = dict(engine=engine, file=path, status="error",
                   error=f"{type(e).__name__}: {e}",
                   trace=traceback.format_exc()[-400:],
                   time=round(time.time() - t0, 3))
    print(json.dumps(out), flush=True)


# ── worker: pyIC3-LLM (clause sideloading) ───────────────────────────
def worker_llm(name, aag, mapf, verilog, hints_json=""):
    import model_encoder, pdr as pdr_mod
    from clause_sideloader import (
        AIGERSymbolMap, PredicateEncoder, LLMOracle,
        load_hints, save_hints, load_llm_config,
        _extract_code_block, _eval_hints_individually,
    )
    import clause_sideloader as _cs

    rec = dict(name=name, aag=aag)
    t_total = time.time()
    try:
        mdl = model_encoder.Model()
        parsed = mdl.parse(aag)
        smap = AIGERSymbolMap(mapf)
        encoder = PredicateEncoder(smap, parsed[1])

        cfg = load_llm_config()
        cached = bool(hints_json) and os.path.exists(hints_json)
        if cached:
            t0 = time.time()
            hints, meta = load_hints(hints_json, encoder)
            rec["hint_source"] = "cached"
            rec["hint_load_time"] = round(time.time() - t0, 3)
            rec["hint_metadata"] = meta
        else:
            verilog_src = open(verilog).read()
            prop_lines = [l.strip() for l in verilog_src.split("\n")
                          if "prop" in l.lower()
                          and any(k in l for k in ("wire", "assign", "assert"))]
            prop_desc = ("Safety property:\n" + "\n".join(prop_lines)
                         if prop_lines else "Bad state unreachable.")
            base_summary = smap.summary()
            with open(mapf) as f:
                raw_map = f.read()
            summary = (base_summary
                       + "\n\n## Raw .map (latch/input table)\n```\n"
                       + raw_map.rstrip() + "\n```")
            oracle = LLMOracle(cfg["api_url"], cfg["api_key"], cfg["model"])
            t0 = time.time()
            raw = oracle.call_llm(verilog_src, prop_desc, summary)
            code = _extract_code_block(raw)
            ns = encoder.build_eval_namespace()
            hints = _eval_hints_individually(code, ns)
            rec["hint_source"] = "llm"
            rec["hint_gen_time"] = round(time.time() - t0, 3)
            rec["hint_metadata"] = {"model": cfg["model"]}
            if hints_json:
                try:
                    save_hints(hints, raw, hints_json,
                               metadata={"model": cfg["model"], "source": verilog})
                except Exception as e:
                    rec["save_error"] = str(e)
        rec["hints_generated"] = len(hints)

        # Wrap sideload_clauses so we capture the post-filter inject count
        # even when silent=True suppresses its verbose print.
        injected_box = {"n": None}
        orig = _cs.sideload_clauses
        def _wrapped(pdr_inst, clauses, verbose=True):
            n = orig(pdr_inst, clauses, verbose=False)
            injected_box["n"] = n
            return n
        _cs.sideload_clauses = _wrapped

        solver = pdr_mod.PDR(*parsed, silent=True)
        buf = io.StringIO()
        t0 = time.time()
        with redirect_stdout(buf), redirect_stderr(buf):
            solver.run(hint_lemmas=hints)
        elapsed = time.time() - t0
        rec["hints_injected"] = injected_box["n"]
        rec.update(
            status="ok",
            verdict=_verdict_from_stdout(buf.getvalue()),
            time=round(elapsed, 3),
            frames=len(solver.frames),
            sat_calls=getattr(solver, "sum_of_sat_call", None),
        )
    except Exception as e:
        rec.update(status="error",
                   error=f"{type(e).__name__}: {e}",
                   trace=traceback.format_exc()[-500:])
    rec["wall"] = round(time.time() - t_total, 3)
    print(json.dumps(rec), flush=True)


# ── orchestrators: spawn workers via subprocess (hard wall timeout) ──
def _spawn_subprocess(args, timeout=TIMEOUT):
    t0 = time.time()
    try:
        cp = subprocess.run([PY, SCRIPT, "worker", *args],
                            capture_output=True, text=True, timeout=timeout)
        line = cp.stdout.strip().splitlines()[-1] if cp.stdout.strip() else ""
        try:
            rec = json.loads(line)
        except Exception:
            rec = dict(status="error", error="no-json",
                       stderr=cp.stderr[-300:], stdout=cp.stdout[-300:])
    except subprocess.TimeoutExpired:
        rec = dict(status="timeout", time=timeout)
    rec["wall_outer"] = round(time.time() - t0, 3)
    return rec


def cmd_baseline():
    out_path = os.path.join(ROOT, "experiment", "baseline_results.json")
    cases = collect_all_benchmarks()
    print(f"Baseline sweep: 3 engines × {len(cases)} = {3 * len(cases)} jobs, "
          f"workers={WORKERS}, timeout={TIMEOUT}s")
    sys.stdout.flush()

    jobs = []
    for sub, name, smt2, aag in cases:
        jobs.append(("mini_ic3",  sub, name, smt2))
        jobs.append(("mini_quip", sub, name, smt2))
        jobs.append(("pyic3",     sub, name, aag))

    results = []
    t0 = time.time()
    with cf.ProcessPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(_spawn_subprocess, ["baseline", j[0], j[3]]): j
                for j in jobs}
        done = 0
        for fut in cf.as_completed(futs):
            engine, sub, name, _ = futs[fut]
            rec = fut.result()
            rec.setdefault("engine", engine)
            rec["name"] = name
            rec["category"] = sub
            results.append(rec)
            done += 1
            print(f"[{done}/{len(jobs)}] {engine:10s} {name:25s} "
                  f"{rec.get('status'):8s} verdict={rec.get('verdict','-'):8s} "
                  f"time={rec.get('time','-')} frames={rec.get('frames','-')} "
                  f"sat={rec.get('sat_calls','-')}")
            sys.stdout.flush()
            with open(out_path, "w") as f:
                json.dump(results, f, indent=2)
    print(f"Total wall: {time.time() - t0:.1f}s -> {out_path}")


def cmd_llm():
    out_path = os.path.join(ROOT, "experiment", "llm_results.json")
    cases = collect_safety_with_verilog()
    print(f"LLM sweep: {len(cases)} safety cases, workers={WORKERS}, "
          f"timeout={TIMEOUT}s")
    sys.stdout.flush()

    results = []
    t0 = time.time()
    with cf.ProcessPoolExecutor(max_workers=WORKERS) as ex:
        futs = {
            ex.submit(_spawn_subprocess, ["llm", c[0], c[1], c[2], c[3], c[4]]): c
            for c in cases
        }
        done = 0
        for fut in cf.as_completed(futs):
            c = futs[fut]
            rec = fut.result()
            rec.setdefault("name", c[0])
            results.append(rec)
            done += 1
            print(f"[{done}/{len(cases)}] {rec.get('name'):25s} "
                  f"src={rec.get('hint_source','-'):6s} "
                  f"gen={rec.get('hints_generated','-')} "
                  f"inj={rec.get('hints_injected','-')} "
                  f"verdict={rec.get('verdict','-'):8s} "
                  f"time={rec.get('time','-')} "
                  f"F={rec.get('frames','-')} "
                  f"SAT={rec.get('sat_calls','-')}")
            sys.stdout.flush()
            with open(out_path, "w") as f:
                json.dump(results, f, indent=2)
    print(f"Total wall: {time.time() - t0:.1f}s -> {out_path}")


def _ric3_one(sub, name, aig):
    t0 = time.time()
    try:
        cp = subprocess.run(["rIC3", "-e", "ic3", aig],
                            capture_output=True, text=True, timeout=TIMEOUT)
        elapsed = round(time.time() - t0, 3)
        m = re.search(r"result:\s*(\w+)", cp.stdout + "\n" + cp.stderr)
        verdict = m.group(1) if m else "unknown"
        return dict(category=sub, name=name, verdict=verdict,
                    time=elapsed, returncode=cp.returncode)
    except subprocess.TimeoutExpired:
        return dict(category=sub, name=name, verdict="timeout", time=TIMEOUT)


def cmd_ric3():
    out_path = os.path.join(ROOT, "experiment", "ric3_results.json")
    # Prefer the L2S-converted .aag in data/, fall back to original/.aig.
    cases = []
    for sub, name, _smt2, aag in collect_all_benchmarks():
        d = os.path.join(BENCH_ROOT, sub, name)
        path = aag if os.path.exists(aag) else os.path.join(
            d, "original", f"{name}.aig")
        if os.path.exists(path):
            cases.append((sub, name, path))
    print(f"rIC3 oracle: {len(cases)} cases, workers={WORKERS}, "
          f"timeout={TIMEOUT}s")
    results = []
    with cf.ProcessPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(_ric3_one, *c): c for c in cases}
        for fut in cf.as_completed(futs):
            r = fut.result()
            results.append(r)
            print(f"  {r['name']:25s} {r['verdict']:10s} {r['time']}s")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"-> {out_path}")


# ── CLI dispatch ─────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(prog="sweep.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("baseline", help="run mini_ic3+mini_quip+pyIC3 on 16 cases")
    sub.add_parser("llm",      help="run pyIC3-LLM on 12 safety cases")
    sub.add_parser("ric3",     help="run rIC3 oracle on 16 cases")
    w = sub.add_parser("worker", help="single-job worker (used internally)")
    w.add_argument("kind", choices=["baseline", "llm"])
    w.add_argument("rest", nargs=argparse.REMAINDER)
    args = p.parse_args()

    if args.cmd == "baseline":
        cmd_baseline()
    elif args.cmd == "llm":
        cmd_llm()
    elif args.cmd == "ric3":
        cmd_ric3()
    elif args.cmd == "worker":
        if args.kind == "baseline":
            engine, path = args.rest[:2]
            worker_baseline(engine, path)
        else:  # llm
            name, aag, mapf, verilog, *tail = args.rest
            hints_json = tail[0] if tail else ""
            worker_llm(name, aag, mapf, verilog, hints_json)


if __name__ == "__main__":
    main()
