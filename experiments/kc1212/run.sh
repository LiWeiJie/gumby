#!/usr/bin/env bash

set -e
set -x

cd /var/scratch/pouwelse/jenkins/workspace/pers/consensus_thesis_kcong/consensus-thesis-code

# substitute the SED_+ words
# sed -i "s/SED_N/$n/" gumby/experiments/kc1212/run.sh
# sed -i "s/SED_T/$t/" gumby/experiments/kc1212/run.sh
# sed -i "s/SED_TRACKER_IP/$(hostname)/" gumby/experiments/kc1212/run.sh
python -m src.node $(( (RANDOM % 10000) + 40000)) SED_N SED_T -v --discovery SED_TRACKER_IP

