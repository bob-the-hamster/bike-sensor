#!/usr/bin/env python3
"""
This script makes sure you stay above a certain threshold of activity
on the bike, and it runs an action if you fall below the threshold for
too long
"""

import os
import re
import time
import argparse

########################################################################

DEFAULT_METRICS_FILE = "/opt/node_exporter_textfiles/bike_sensor.prom"
DEFAULT_TARGET = 65.0

########################################################################

class KeepUpThePace():
    
    def __init__(self, metric_name="bike_sensor_petal_count", metrics_from=DEFAULT_METRICS_FILE, target_threshold=DEFAULT_TARGET):
        if not os.path.exists(metrics_from):
            raise Exception(f"Metrics file {metrics_from} does not exist yet")
        self.metrics = MetricsFromFile(metric_name, metrics_from, time_window=15.0)
        self.target = target_threshold
        self.tstate = ThresholdState()
        self.wstate = WarningState()

    def run(self):
        while True:
            rpm = self.metrics.rpm()
            if rpm is None:
                rpm = -1.0
            # Update target state based on RPM
            if rpm < self.target:
                self.tstate.set("slow")
            else:
                self.tstate.set("ok")
            # Update warning state
            if self.wstate.check("ok") and self.tstate.check_over("slow", 5.0):
                self.wstate.set("warning")
            if self.tstate.check("ok"):
                self.wstate.set("ok")
            if self.wstate.check_over("warning", 15.0):
                self.wstate.set("consequences")
            print(f"{rpm:0.2f}rpm - {self.tstate.show()} {self.wstate.show()}")
            time.sleep(1.0) 
    
########################################################################

class BaseState():
    
    def __init__(self, valid_values, initial_value=None):
        self.valid_values = valid_values
        self.value = None
        self.set(initial_value)
    
    def set(self, value):
        if value not in self.valid_values and value is not None:
            raise Exception(f"Value {repr(value)} is not in {self.valid_values}")
        if self.value != value:
            old = self.value
            self.last_change = time.time()
            self.value = value
            self.onchange(old, value)
    
    def age(self):
        return time.time() - self.last_change

    def check(self, check_state):
        return self.value == check_state
    
    def check_over(self, check_state, over_age):
        return self.value == check_state and self.age() > over_age
    
    def show(self):
        return f"{self.__class__.__name__}:{self.value}:{self.age():0.1f}"
    
    def onchange(self, oldval, newval):
        print(f"{self.__class__.__name__} change {oldval} -> {newval}")

class ThresholdState(BaseState):
    
    def __init__(self):
        super().__init__(["slow", "ok"])
        
class WarningState(BaseState):
    
    def __init__(self):
        super().__init__(["ok", "warning", "consequences"], "ok")

########################################################################

class MetricsFromFile():
    
    def __init__(self, metric_name, filename, time_window):
        self.metric_name = metric_name
        self.filename = filename
        self.time_window = time_window
        self.samples = []
        self.pattern = re.compile(f"^{re.escape(metric_name)} (\d+)$")
    
    def rpm(self):
        result = None
        sample = self.read_sample()
        if sample:
            now, nowval = sample
            before_i = self.find_sample_before(now, self.time_window)
            if before_i is not None:
                before, beforeval = self.samples[before_i]
                seconds_diff = now - before
                val_diff = nowval - beforeval
                rps = val_diff / seconds_diff
                result = rps * 60.0
                # trim the samples
                self.samples = self.samples[before_i:]
            self.samples.append(sample)
        return result
    
    def read_sample(self):
        with open(self.filename, "r") as f:
            for line in f.readlines():
                match = self.pattern.match(line.strip())
                if match:
                    counter = int(match.group(1))
                    return (time.time(), counter)
        return None
    
    def find_sample_before(self, before_when, how_many_seconds):
        # search backwards through the samples to find one that is the correct age
        for i in reversed(range(len(self.samples))):
            (t, v) = self.samples[i]
            diff = before_when - t
            if diff > how_many_seconds:
                return i
        # Didn't find a sample that was old enough, so use the oldest sample available
        if len(self.samples) > 0:
            return 0
        # No samples available at all
        return None


########################################################################

def command_line_entry_point():
    parser = argparse.ArgumentParser(description="Run actions if the bike sensor isn't keeping above a given RPM")
    parser.add_argument("-f", "--filename", default=DEFAULT_METRICS_FILE, help="Text file to read the metrics from")
    parser.add_argument("-t", "--target", metavar="RPM", default=DEFAULT_TARGET, type=float, help="Target RPM threshold to stay above")
    opts = parser.parse_args()
    app = KeepUpThePace(metrics_from=opts.filename, target_threshold=opts.target)
    app.run()

if __name__ == "__main__":
    command_line_entry_point()
