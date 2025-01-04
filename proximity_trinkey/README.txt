This code is meant to run on a Adafruit Proximity Trinkey with
CircuitPython installed.

See https://learn.adafruit.com/adafruit-proximity-trinkey to learn more

The purpose of this code is to count petal revolutions on a stationary
bicycle by detecting the movement of one foot when it passes within
range of the sensor.

It outputs metrics to the serial console where a companion program
(bikehost) can read them.

The files at ./circuitpy/lib/* are dependencies from
adafruit-circuitpython-bundle-9.x
