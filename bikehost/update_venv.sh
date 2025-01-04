#!/bin/bash

SCRIPTDIR=$(dirname $0)

cd "$SCRIPTDIR"

# Check if we are already in a venv
IN_VENV=$(python3 -c 'import sys; print(sys.prefix != sys.base_prefix)')
if [ "$IN_VENV" = "True" ] ; then
  echo "Please deactivate the venv first before you update it. Use command: deactivate"
  exit 1
fi

# If the venv doesn't exist, create it.
if [ ! -d "venv" ] ; then
  python3 -m venv ./venv
fi

# Activate the venv (just for this script) and install pip requirements
source ./venv/bin/activate
python3 -m pip install -U -r ./requirements.txt

echo "Done, you can re-activate your venv now with: source venv/bin/activate"
