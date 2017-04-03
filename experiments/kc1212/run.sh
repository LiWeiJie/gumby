#!/usr/bin/env bash

set -e
set -x

cd /var/scratch/pouwelse/jenkins/workspace/pers/consensus_thesis_kcong/consensus-thesis-code

python -m src.node SED_N SED_T -v --discovery SED_TRACKER_IP

