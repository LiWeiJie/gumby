#!/usr/bin/env bash

set -e
set -x

cd /var/scratch/pouwelse/jenkins/workspace/pers/consensus_thesis_kcong/consensus-thesis-code

let "n = $DAS4_INSTANCES_TO_RUN"
let "t = (n-1)/3"
python -m src.node 4 "$t" -v --discovery "$TRACKER_IP"

