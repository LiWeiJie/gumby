#!/usr/bin/env bash

set -e
set -x

pwd
cd /var/scratch/pouwelse/jenkins/workspace/pers/test_consensus_weijie/consensus-code

# e.g. python -m src.discovery -n SED_N -t SED_T -m "$DAS4_INSTANCES_TO_RUN" --inst SED_DELAY SED_EXPERIMENT SED_PARAM
DISCOVERY_COMMAND