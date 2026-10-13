#!/usr/bin/env bash
# Download the official Stockfish Linux build (x86-64, AVX2) into ./stockfish/ and print the
# line to add to your shell setup. On other systems, install Stockfish yourself and set STOCKFISH.
set -euo pipefail
URL="https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.tar"
mkdir -p stockfish
curl -fsSL "$URL" -o stockfish/stockfish.tar
tar -xf stockfish/stockfish.tar -C stockfish
BIN=$(find "$PWD/stockfish" -type f -name 'stockfish-ubuntu-x86-64-avx2' | head -n 1)
chmod +x "$BIN"
echo "Stockfish is at: $BIN"
echo "Add this to your shell setup:  export STOCKFISH=$BIN"
