#!/usr/bin/env bash

set -e
set -x

cd /var/scratch/pouwelse/jenkins/workspace/pers/consensus_thesis_kcong/consensus-thesis-code

# substitute the SED_+ words:
# sed -i run_discovery.sh 's/SED_N/4'
# sed -i run_discovery.sh 's/SED_T/1'
# sed -i run_discovery.sh 's/SED_DELAY/10'
# sed -i run_discovery.sh 's/SED_EXPERIMENT/bootstrap'
python -m src.discovery -n SED_N -t SED_T -m "$DAS4_INSTANCES_TO_RUN" -v \
    --inst SED_DELAY SED_EXPERIMENT

