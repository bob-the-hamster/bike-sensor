# Standard library
import time
import random

# Adafruit bundle libraries
import board
import neopixel
from adafruit_apds9960.apds9960 import APDS9960

print("Proximity Trinkey Practice")

i2c = board.I2C()  # uses board.SCL and board.SDA
apds = APDS9960(i2c)
apds.enable_proximity = True

pixels = neopixel.NeoPixel(board.NEOPIXEL, 2)

class WanderColor():

    def __init__(self):
        self._color = 128
        self._dir = 0

    def color(self):
        self.wander()
        return self._color

    def wander(self):
        c = self._color
        d = self._dir
        d = min(max(d + random.randint(-1, 1), -5), 5)
        c += d
        c = min(max(c, 0), 255)
        self._color = c
        self._dir = d

def scale_rgb(r, g, b, scale=1.0):
    if scale > 1.0 or scale < 0.0:
        raise Exception("scale_rgb only supports range 0.0 to 1.0")
    return (int(r * scale), int(g * scale), int(b * scale))

red = WanderColor()
green = WanderColor()
blue = WanderColor()

checkin = 0.0
while True:
    (r, g, b) = scale_rgb(red.color(), green.color(), blue.color(), 0.1)
    pixels.fill((r, g, b))
    delay = 0.01
    time.sleep(delay)
    checkin += delay
    if checkin > 1.0:
        checkin -= 1.0
        print(f"Color = {r}, {g}, {b}, Proximity = {apds.proximity}")
