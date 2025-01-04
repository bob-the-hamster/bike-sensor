#!/usr/bin/env python3

"""
This exporter runs on the same host where the Adafruit Proximity Sensor
Trinkey is attached. It reads lines of text in Prometheus format from
a serial device, and makes them available on an http port that can be
scraped by prometheus or other tools.
"""

import serial
ser = serial.Serial("/dev/ttyACM0", timeout=10.0)
while True:
     cc = str(ser.readline())
     print(cc[2:][:-5])

