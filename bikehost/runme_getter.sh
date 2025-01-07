#!/bin/bash

# Run the getter inside a python virtualenv

SCRIPTDIR=$(dirname $0)
cd "$SCRIPTDIR"

# Check if we are already in a venv
IN_VENV=$(python3 -c 'import sys; print(sys.prefix != sys.base_prefix)')
if [ "$IN_VENV" = "True" ] ; then
  echo "You are already inside a venv, this script activates its own venv."
  exit 1
fi

./update_venv.sh
source ./venv/bin/activate
./serial_metrics_getter.py
