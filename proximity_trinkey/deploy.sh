#!/bin/bash

# CircuitPython code is deployed to an Adafruit device by simply copying
# the files to the mounted USB storage. The code runs automatically.

SCRIPTDIR=$(dirname $0)
cd "$SCRIPTDIR"

# Guess the location of the mounted storage.
USBMOUNT=$( mount | grep "CIRCUITPY" | cut -d " " -f 3 | grep "CIRCUITPY" )

# Copy over the files.
# If unwanted files need to be removed you need to clean that up manually
cp -r ./circuitpy/* "${USBMOUNT}"/

# The code.py file will execute automatically on the Adafruit device
# Any errors will go to the serial terminal, so they will be visible
# in the logging output of the bikehost companion program
