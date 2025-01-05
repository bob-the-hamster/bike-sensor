# Standard library
import time
import random

# Adafruit bundle libraries
import board
import neopixel
from adafruit_apds9960.apds9960 import APDS9960

print("\nAdafruit Proximity Trinkey - Count how often anything passes the sensor")

#### Objects

class ProximityCounter():

    def __init__(self):
        # Set up the adps object representing the proximity sensor
        i2c = board.I2C()  # uses board.SCL and board.SDA
        self.apds = APDS9960(i2c)
        self.apds.enable_proximity = True
        
        # Set up the pixels for visual feedback that the sensor is working
        self.pixels = neopixel.NeoPixel(board.NEOPIXEL, 2)
        self.blinker = BlinkHandler(self.pixels)
        self.blinker.blink_color((0, 255, 0), 1.0)
        
        # Set up the counter
        self.count = 0
        self.last_output = time.monotonic()
        self.something_there = False
        self.something_time = 0.0

    def run(self):
        while True:
            self.update_detection_state_machine()
            self.blinker.update()
            if not self.blinker.blinking():
                self.pixels.fill((self.apds.proximity, 0, 0))
            self.update_output()
    
    def update_output(self):
        delta = time.monotonic() - self.last_output
        if delta >= 1.0:
            print(f"{time.monotonic()} Count = {self.count} Proximity={self.apds.proximity}")
            self.last_output = time.monotonic()

    def update_detection_state_machine(self):
        if self.something_there:
            # Something was there, check to see if it is gone
            if self.apds.proximity == 0:
                self.something_there = False
        else:
            # Nothing there, check to see if something has appeared
            if self.apds.proximity > 0:
                self.count += 1
                self.something_there = True

class BlinkHandler():
    
    def __init__(self, pixels):
        self.pixels = pixels
        self.off_in = 0.0
        self.color = (128, 128, 128)
        self.last_update = time.monotonic()
    
    def blinking(self):
        return self.off_in > 0.0
    
    def blink_color(self, color_tuple, seconds):
        # Start a blink now, overwrites any current blink
        self.color = color_tuple
        self.off_in = seconds

    def update(self):
        t = time.monotonic()
        delta = t - self.last_update
        self.last_update = t
        if self.off_in > 0.0:
            self.off_in -= delta
            if self.off_in <= 0.0:
                self.color = (0, 0, 0)
        self.pixels.fill(self.color)

#### Init

obj = ProximityCounter()
obj.run()
