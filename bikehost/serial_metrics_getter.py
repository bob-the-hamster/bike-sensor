#!/usr/bin/env python3

"""
This exporter runs on the same host where the Adafruit Proximity Sensor
Trinkey is attached. It reads lines of text in Prometheus format from
a serial device, and dumps them to text files where it is easy for
prometheus node_exporter to read them.
"""

import serial
import re
import os

########################################################################


class SerialSensorExporter():
    
    def __init__(self):
        self.textfile_name = "bike_sensor.txt"
        
        # You would tell node_exporter to scrape this folder with:
        # --collector.textfile.directory="/opt/node_exporter_textfiles/" 
        self.dest_dir = "/opt/node_exporter_textfiles/"
        
        if not os.access(self.dest_dir, os.W_OK):
            print(f"Textfile directory {repr(self.dest_dir)} is not writable. Falling back to the current directory")
            self.dest_dir = "./"
        
        self.ser = serial.Serial("/dev/ttyACM0", timeout=10.0)
        
        # Letters numbers and underscore, followed by a number with an
        # optional decimal part. We don't attempt to support timestamps
        # in the data.
        self.pattern = re.compile("^[a-zA-Z_][a-zA-Z0-9_]* \d+(\.\d+)?$")
    
    def run(self):
        while True:
             cc = str(self.ser.readline())
             line = cc[2:][:-5]
             print(line)
             if self.pattern.match(line):
                 self.write_metric(line)
    
    def write_metric(self, line):
        filename = os.path.join(self.dest_dir, self.textfile_name)
        with open(filename, "w") as f:
            f.write(line + "\n")

########################################################################

def command_line_entry_point():
    exporter = SerialSensorExporter()
    exporter.run()

if __name__ == "__main__":
    command_line_entry_point()
