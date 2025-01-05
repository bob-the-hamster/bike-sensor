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
        
        # Set up the output
        self.last_output = time.monotonic()
        
        # Set up the detection state machine
        self.detector = DetectionStateMachine(self.apds)


    def run(self):
        while True:
            self.count += self.detector.update()
            self.blinker.update()
            if not self.blinker.blinking():
                self.pixels.fill((self.apds.proximity, 0, 0))
            self.update_output()
    
    def update_output(self):
        delta = time.monotonic() - self.last_output
        if delta >= 1.0:
            print(f"{time.monotonic()} Count={self.count} Prox={self.apds.proximity} State={self.detector.state} Dura={self.detector.duration}")
            self.last_output = time.monotonic()

class DetectionStateMachine():
    
    def __init__(self, apds):
        self.apds = apds
        self.state = "NOTHING"
        self.start_time = time.monotonic()
        self.end_time = time.monotonic()
        self.duration = None

    def update(self):
        # Returns 1 if the count has gone up in this cycle
        result = 0
        if self.state == "SOMETHING":
            # Something was there, check to see if it is gone
            if self.apds.proximity == 0:
                self.state = "NOTHING"
                t = time.monotonic()
                self.duration = t - self.start_time
                self.end_time = t
        elif self.state == "NOTHING":
            # Nothing there, check to see if something has appeared
            self.start_time = time.monotonic()
            dist = self.apds.proximity
            if dist == 1:
                self.state = "UNCERTAIN"
            elif dist > 1:
                self.state = "SOMETHING"
                result = 1
        elif self.state == "UNCERTAIN":
            # A Weak detection should not flip state, we just wait for
            # it to get stronger or to go away
            dist = self.apds.proximity
            if dist == 0:
                self.state = "NOTHING"
            elif dist > 1:
                self.state = "SOMETHING"
                result = 1
        else:
            print(f"Unknown state {repr(self.state)}")
            self.state = "NOTHING"
        return result

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
