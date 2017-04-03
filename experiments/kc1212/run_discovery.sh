#!/usr/bin/env bash

set -e
set -x

cd /var/scratch/pouwelse/jenkins/workspace/pers/consensus_thesis_kcong/consensus-thesis-code

# substitute the SED_+ words
# sed -i "s/SED_N/$n/" gumby/experiments/kc1212/run_discovery.sh
# sed -i "s/SED_T/$t/" gumby/experiments/kc1212/run_discovery.sh
# sed -i "s/SED_DELAY/$delay/" gumby/experiments/kc1212/run_discovery.sh
# sed -i "s/SED_EXPERIMENT/bootstrap/" gumby/experiments/kc1212/run_discovery.sh
python -m src.discovery -n SED_N -t SED_T -m "$DAS4_INSTANCES_TO_RUN" \
    --inst SED_DELAY SED_EXPERIMENT

