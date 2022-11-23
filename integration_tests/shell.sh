#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

python=${PYTHON:-$(which python3)}

_venv=${VENV_PATH:-./.venv}

# ensure virtual env for test dependencies
[ -d $_venv ] || $python -m venv $_venv

# activate venv and install test python dependencies
source ${_venv}/bin/activate

${_venv}/bin/python -m pip install -r test-requirements.txt

# other system dependencies assumed available for integration tests:
# * docker-compose
# * docker or equivalent

# path to denv executable
denv=${DENV:-${WAZO_ROOT:-$HOME/wazo}/denv/denv}
source ${denv}

project=confgend
asset=${ASSET:-base}
compose_project="${project}_${asset}"

# todo: change when denv is fixed to set project name properly to ${projectname}_${assets_name}
denv enter $compose_project ${asset}

function cleanup(){
    denv exit $compose_project ${asset}
    deactivate
}

# cleanup docker-compose environment on exit
trap cleanup EXIT

# execute command, defaulting to shell
${@:-$SHELL}
