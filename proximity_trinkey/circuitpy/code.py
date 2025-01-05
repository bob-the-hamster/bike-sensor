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

    def __init__(self, metric_name="bike_sensor_petal_count", verbose=True):
        self.metric_name = metric_name
        self.verbose = verbose
        
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
                self.visualize_proximity()
            self.update_output()
    
    def visualize_proximity(self):
        prox = self.apds.proximity
        if prox == 1:
            rgb = (1, 0, 0)
        else:
            rgb = (0, 0, prox)
        self.pixels.fill(rgb)
    
    def update_output(self):
        delta = time.monotonic() - self.last_output
        if delta >= 1.0:
            if self.verbose:
                print(f"{time.monotonic()} Count={self.count} Prox={self.apds.proximity} Dura={self.detector.duration}")
            print(f"{self.metric_name} {self.count}")
            self.last_output = time.monotonic()

class DetectionStateMachine():
    
    def __init__(self, apds):
        self.apds = apds
        self.state = self.state_nothing
        self.start_time = time.monotonic()
        self.end_time = time.monotonic()
        self.duration = None

    def state_something(self):
        # Something was there, check to see if it is gone
        if self.apds.proximity == 0:
            self.state = self.state_nothing
            t = time.monotonic()
            self.duration = t - self.start_time
            self.end_time = t
        return 0
        
    def state_nothing(self):
        # Nothing there, check to see if something has appeared
        self.start_time = time.monotonic()
        dist = self.apds.proximity
        if dist == 1:
            self.state = self.state_uncertain
        elif dist > 1:
            self.state = self.state_something
            return 1
        return 0
        
    def state_uncertain(self):
        # A Weak detection should not flip state, we just wait for
        # it to get stronger or to go away
        dist = self.apds.proximity
        if dist == 0:
            self.state = self.state_nothing
        elif dist > 1:
            self.state = self.state_something
            return 1
        return 0

    def update(self):
        # Returns 1 if the count has gone up in this cycle
        return self.state()

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
