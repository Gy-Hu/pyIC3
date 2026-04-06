import sys
import time
import model_encoder
import pdr

if len(sys.argv) < 2:
    print("Usage: python run_silent.py <file.aag>")
    sys.exit(1)

file = sys.argv[1]
m = model_encoder.Model()

start_time = time.time()
solver = pdr.PDR(*m.parse(file), silent=True)
solver.run()
end_time = time.time()

print(f"Time: {end_time - start_time:.3f}s")
