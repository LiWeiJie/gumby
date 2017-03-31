#!/usr/bin/env bash

set -e
set -x

cd /var/scratch/pouwelse/jenkins/workspace/pers/consensus_thesis_kcong/consensus-thesis-code

let "m = $DAS4_INSTANCES_TO_RUN"
python -m src.discovery -n 4 -t 1 -m "$m" -v --inst 10 bootstrap

