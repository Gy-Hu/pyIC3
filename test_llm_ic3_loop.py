#!/usr/bin/env python3
"""
Test: LLM embedded into IC3 loop for toy_lock_4.

Strategy: IC3 runs normally. Each time it creates a new frame (= made progress),
we call LLM with the current proof state and ask for targeted hints.
The hints are verified (Tier 0 + Tier 2/3) and injected into frames.
IC3 continues with the new lemmas.
"""

import model_encoder, pdr, time, signal, sys
from llm_oracle import (AIGERSymbolMap, PredicateEncoder, LLMOracle,
                         load_llm_config, _extract_code_block)
from z3 import *

cfg = load_llm_config()
TIMEOUT = int(sys.argv[1]) if len(sys.argv) > 1 else 60

aag = 'blocksys-benchmark/converted_with_map/toy_lock_4.aag'
mapf = 'blocksys-benchmark/converted_with_map/toy_lock_4.map'
vf = 'blocksys-benchmark/original/toy_lock_4/toy_lock.v'
verilog_src = open(vf).read()

# Parse model and build encoder
m_ref = model_encoder.Model()
r_ref = m_ref.parse(aag)
smap = AIGERSymbolMap(mapf)
enc = PredicateEncoder(smap, r_ref[1])
ns = enc.build_eval_namespace()

oracle = LLMOracle(cfg['api_url'], cfg['api_key'], 'claude-opus-4-6')

# Track conversation for multi-turn context
llm_messages = [
    {"role": "system", "content": """You are helping IC3/PDR prove a distributed lock protocol.
IC3 will tell you its current state (frames, lemmas, push rate). Generate
STRONG composite clauses that are individually relatively-inductive.

Each clause must be self-sustaining: Or(condition, guard_reason).
Use: bool_var, word_eq_zero, word_neq_zero, word_eq, word_neq, word_lt, word_gt.
1-bit vars (held_0..3) used directly. Return `hints = [...]`."""},
    {"role": "user", "content": f"""Protocol:
```verilog
{verilog_src}
```
Safety: locked_i==0 or locked_i!=locked_j for all i!=j.
Variables: {smap.summary()}

IC3 is about to start. Generate initial hints to seed the proof."""}
]

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {cfg['api_key']}"}
import requests

def llm_callback(frame_info, latest_lemmas):
    """Called by IC3 when a new frame is created."""
    user_msg = f"""IC3 status: {frame_info['num_frames']} frames, {frame_info['total_sat_calls']} SAT calls, push rate {frame_info['push_rate']}.
Lemmas per frame: {frame_info['lemmas_per_frame']}
Recent lemmas (from deepest frame): {latest_lemmas[:3]}

Generate MORE targeted hints to help IC3 push further. Focus on clauses
about epoch ordering and transfer relationships that IC3 hasn't discovered yet.
Return `hints = [...]`."""

    llm_messages.append({"role": "user", "content": user_msg})

    try:
        resp = requests.post(cfg['api_url'], json={
            "model": "claude-opus-4-6",
            "messages": llm_messages[-6:],  # keep context manageable
            "temperature": 0.3,
            "max_tokens": 3000,
        }, headers=headers, timeout=120)
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]
        llm_messages.append({"role": "assistant", "content": raw})
    except Exception as e:
        print(f"  [LLM callback] API error: {e}")
        return []

    try:
        code = _extract_code_block(raw)
        local_ns = dict(ns)
        exec(code, local_ns)
        hints = local_ns.get('hints', [])
        print(f"  [LLM callback] Got {len(hints)} new hints at frame {frame_info['num_frames']}")
        return hints
    except Exception as e:
        print(f"  [LLM callback] Parse error: {e}")
        return []


# Get initial hints
print("Getting initial LLM hints...")
try:
    resp = requests.post(cfg['api_url'], json={
        "model": "claude-opus-4-6",
        "messages": llm_messages,
        "temperature": 0.3,
        "max_tokens": 3000,
    }, headers=headers, timeout=120)
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"]
    llm_messages.append({"role": "assistant", "content": raw})
    code = _extract_code_block(raw)
    local_ns = dict(ns)
    exec(code, local_ns)
    initial_hints = local_ns.get('hints', [])
    print(f"Initial: {len(initial_hints)} hints")
except Exception as e:
    print(f"Initial hint generation failed: {e}")
    initial_hints = []

# Run IC3 with LLM callback
m = model_encoder.Model()
result = m.parse(aag)
solver = pdr.PDR(*result, silent=True)
solver._llm_callback = llm_callback

class TO(Exception):
    pass
def alarm_h(s, f):
    raise TO()

signal.signal(signal.SIGALRM, alarm_h)
signal.alarm(TIMEOUT)
try:
    t0 = time.time()
    solver.run(hint_lemmas=initial_hints)
    signal.alarm(0)
except TO:
    signal.alarm(0)
signal.signal(signal.SIGALRM, signal.SIG_DFL)

elapsed = time.time() - t0
frames = len(solver.frames)
print(f"\nResult: {elapsed:.1f}s  frames={frames}  sat={solver.sum_of_sat_call}")
print(f"  lemmas/frame: {[len(f.Lemma) for f in solver.frames]}")
print(f"  push={solver.successful_pushes}/{solver.total_push_attempts}")
print(f"  LLM callbacks: {solver._llm_call_count}")
# Output just the frame count for autoresearch metric
print(f"METRIC:{frames}")
