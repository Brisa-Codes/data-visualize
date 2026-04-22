#!/bin/bash
# demo.sh - End to End test for ViralViz Engine

echo "==================================================="
echo "         Running ViralViz Engine Demo"
echo "==================================================="

# Note: In a real environment, you'd provide actual paths to music/sfx.
# This tests the dual-format output capability using the example CSV.

python ../main.py --input demo.csv --format both --style dark --speed fast --output ../renders

echo "==================================================="
echo "                Demo Finished."
echo "==================================================="
