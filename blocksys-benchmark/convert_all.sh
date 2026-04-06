#!/bin/zsh
# Convert all 12 BlockSys benchmarks: Verilog → aigmap → ABC optimize → fold → .aag + .map
ORIG="original"
OUT="converted_with_map"
mkdir -p "$OUT"

typeset -A BENCHMARKS
BENCHMARKS=(
  client_server       "client_server/client_server.v|client_server"
  toy_lock_4          "toy_lock_4/toy_lock.v|toy_lock"
  h_Dekker            "h_Dekker/main.v|main"
  h_Arbiter           "h_Arbiter/main.v|main"
  h_TreeArb           "h_TreeArb/main.sv|main"
  cache_coherence_two "cache_coherence_two/two_processor_bin_2.v|main"
  cache_coherence_three "cache_coherence_three/three_processor_bin_2.v|main"
  sw_state_machine    "sw_state_machine/sw_state_machine.v|sw_state_machine"
  h_Vending           "h_Vending/main.sv|main"
  Heap                "Heap/main.v|main"
  h_CRC               "h_CRC/main.sv|main"
  h_FIFO              "h_FIFO/main.v|main"
)

for name in ${(k)BENCHMARKS}; do
  val="${BENCHMARKS[$name]}"
  srcfile="${val%%|*}"
  topmod="${val##*|}"
  ext="${srcfile##*.}"
  echo "=== $name (top=$topmod) ==="

  if [ "$ext" = "sv" ]; then
    READ_CMD="read_verilog -sv -formal"
  else
    READ_CMD="read_verilog -formal"
  fi

  # Step 1: Yosys aigmap
  yosys -q -p "
    $READ_CMD $ORIG/$srcfile;
    prep -top $topmod;
    chformal -lower;
    flatten;
    memory -nordff;
    setundef -undriven -init -expose;
    setundef -anyseq;
    delete -output;
    techmap;
    aigmap;
    write_aiger -zinit -symbols -map $OUT/${name}.map $OUT/${name}_raw.aig
  " 2>/dev/null
  if [ $? -ne 0 ]; then
    echo "  SKIP (aigmap failed)"
    continue
  fi

  # Step 2: ABC optimize
  yosys-abc -c "read_aiger $OUT/${name}_raw.aig; balance; rewrite; refactor; balance; rewrite; refactor; balance; rewrite; refactor; write_aiger $OUT/${name}_opt.aig" > /dev/null 2>&1

  # Step 3: Fold bad→output
  yosys-abc -c "&r $OUT/${name}_opt.aig; &put; fold; write_aiger $OUT/${name}.aig" > /dev/null 2>&1

  # Step 4: AAG
  aigtoaig "$OUT/${name}.aig" "$OUT/${name}.aag" 2>/dev/null

  if [ -f "$OUT/${name}.aag" ]; then
    header=$(head -1 "$OUT/${name}.aag")
    echo "  OK: $header"
  else
    echo "  FAIL"
  fi

  rm -f "$OUT/${name}_raw.aig" "$OUT/${name}_opt.aig"
done
