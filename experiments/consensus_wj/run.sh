#!/usr/bin/env bash

set -e
set -x

cd /var/scratch/pouwelse/jenkins/workspace/pers/test_consensus_weijie/consensus-code

export LIBRARY_PATH="$LIBRARY_PATH:/home/pouwelse/erasure/lib"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/home/pouwelse/erasure/lib"

# debug
printenv
pwd
echo "$OUTPUT_DIR"

# .e.g python -m src.node 0 4 1 -v --discovery 127.0.0.1 --fan-out 10 --consensus-delay 90
NODE_COMMAND