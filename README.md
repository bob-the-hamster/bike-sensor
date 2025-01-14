# Bike Sensor

This code is designed to use an Adafruit Proximity Trinkey to sense the
revolutions of one of the petals of a stationary bicycle. It counts
how many revolutions have been made, and makes them available as
prometheus metrics for node_exporter to pick up.

The `proximity_trinky` folder contains CircuitPython code to load onto
the Adafruit device. See also the README in that folder

The `bikehost` folder contains python code to run on the Linux computer
where the Adafruit devices is attached via usb cable.

To collect the metrics into prometheus, you can use node-exporter.
To graph the metrics from the sensor in prometheus, or a compatable
tool like Grafana, use the query:

```
rate(bike_sensor_petal_count[1m]) * 60
```
