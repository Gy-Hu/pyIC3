#!/usr/bin/env python3
"""Compare vanilla vs CEGIS-hint IC3 on toy_lock_4 using multiprocessing timeout."""
import multiprocessing, time, sys

TIMEOUT = int(sys.argv[1]) if len(sys.argv) > 1 else 120
AAG = 'blocksys-benchmark/converted_with_map/toy_lock_4.aag'
MAP = 'blocksys-benchmark/converted_with_map/toy_lock_4.map'
HINTS = 'blocksys-benchmark/converted_with_map/toy_lock_4_hints.json'

def worker(aag, mapf, hints_file, result_queue):
    import model_encoder, pdr
    from llm_oracle import AIGERSymbolMap, PredicateEncoder, load_hints

    m = model_encoder.Model(); r = m.parse(aag)
    hints = None
    if hints_file and mapf:
        smap = AIGERSymbolMap(mapf)
        enc = PredicateEncoder(smap, r[1])
        hints, _ = load_hints(hints_file, enc)

    s = pdr.PDR(*r, silent=True)
    t0 = time.time()
    try:
        s.run(hint_lemmas=hints)
    except Exception:
        pass
    result_queue.put({
        'time': round(time.time() - t0, 1),
        'frames': len(s.frames),
        'sat': s.sum_of_sat_call,
        'push': f'{s.successful_pushes}/{s.total_push_attempts}',
        'lemmas': [len(f.Lemma) for f in s.frames],
        'propagate': round(s.sum_of_propagate_time, 1),
        'mic': round(s.sum_of_mic_time, 1),
    })

def run_with_timeout(label, aag, mapf, hints_file):
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=worker, args=(aag, mapf, hints_file, q))
    p.start()
    p.join(TIMEOUT + 10)
    if p.is_alive():
        p.terminate(); p.join()
    r = q.get() if not q.empty() else {'time': TIMEOUT, 'frames': 0, 'sat': 0, 'push': '?', 'lemmas': [], 'propagate': 0, 'mic': 0}
    print(f'{label}: {r["time"]}s  F={r["frames"]}  SAT={r["sat"]}  push={r["push"]}')
    print(f'  lemmas: {r["lemmas"]}')
    print(f'  propagate={r["propagate"]}s  mic={r["mic"]}s')
    return r

if __name__ == '__main__':
    print(f'Timeout: {TIMEOUT}s\n')
    r1 = run_with_timeout('Vanilla ', AAG, None, None)
    print()
    r2 = run_with_timeout('W/Hints ', AAG, MAP, HINTS)
    print(f'\nDelta: F {r1["frames"]}→{r2["frames"]}  SAT {r1["sat"]}→{r2["sat"]}')
