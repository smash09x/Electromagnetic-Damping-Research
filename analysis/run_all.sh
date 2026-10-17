#!/usr/bin/env bash
# Reproduce every number and figure in the paper from the raw data.
# Requires: python3 with numpy, scipy, matplotlib.  Run from anywhere.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$HERE/.."
cd "$HERE"
echo "[1/4] clock calibration from mains hum";  python3 clock_cal.py "$HERE" "$ROOT" clock.json | head -1
cd round2 && mkdir -p out
echo "[2/4] alternative estimators";             python3 refit.py >/dev/null; python3 physfit.py >/dev/null
echo "[3/4] final clock-corrected table + stats"; python3 final.py >/dev/null; python3 final2.py >/dev/null; python3 final3.py >/dev/null
cp final_table.csv final_stats.json .. 2>/dev/null || true
cd "$HERE"
echo "[4/4] figures";                             python3 make_final_figs.py "$HERE" "$ROOT" final_table.csv final_stats.json "$ROOT/paper/figs"
echo "done: analysis/final_table.csv, analysis/final_stats.json, paper/figs/*.pdf"
