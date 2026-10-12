#!/bin/sh
# Build the AGC emulator (yaAGC, with the Discovery trace patch), the
# assembler (yaYUL), and assemble Luminary 099 from its source.
# Needs: gcc, make not required. Linux or macOS. Takes about a minute.
set -e
cd "$(dirname "$0")/virtualagc"

echo "== yaAGC (emulator, patched)"
cd yaAGC
gcc -O2 -pthread -DGDBMI -DNVER= '-DINSTALLDIR="/usr/local/bin"' -o yaAGC \
    main.c agc_cli.c agc_simulator.c agc_debugger.c agc_gdbmi.c \
    agc_disassembler.c agc_help.c nbfgets.c agc_symtab.c NormalizeSourceName.c \
    agc_engine_init.c agc_engine.c agc_utilities.c rfopen.c Backtrace.c \
    SocketAPI.c DecodeDigitalDownlink.c ../Tools/checkdec.c -lm 2>&1 | grep -i " error" || true
test -x yaAGC
cd ..

echo "== yaYUL (assembler)"
cd yaYUL
gcc -O2 -DNVER= -o yaYUL *.c -lm 2>&1 | grep -i " error" || true
test -x yaYUL
cd ..

echo "== Luminary 099 (assemble the rope from source)"
cd Luminary099
../yaYUL/yaYUL MAIN.agc > assembly.log 2>&1
test -f MAIN.agc.bin
echo "   MAIN.agc.bin    $(wc -c < MAIN.agc.bin) bytes (36864 words, 16 bits each)"
echo "   MAIN.agc.symtab the symbol table, for the emulator's debugger"
cd ..

echo "done"
