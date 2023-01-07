#!/usr/bin/env python3

import logging
import sys

from prometheus_client import Gauge, start_http_server

from . import config, dht, meter

co2_gauge = Gauge("co2", "CO2 levels in PPM", ["sensor"])
temp_gauge = Gauge("temperature", "Temperature in C", ["sensor"])
humidity_gauge = Gauge("humidity", "Humidity in RH%", ["sensor"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def co2_callback(sensor, value):
    if sensor == meter.CO2METER_CO2:
        co2_gauge.labels("co2mini").set(value)
    elif sensor == meter.CO2METER_TEMP:
        temp_gauge.labels("co2mini").set(value)
    elif sensor == meter.CO2METER_HUM:
        humidity_gauge.labels("co2mini").set(value)


def dht_callback(results):
    if "temperature" in results:
        temp_gauge.labels("dht").set(results["temperature"])
    if "humidity" in results:
        humidity_gauge.labels("dht").set(results["humidity"])


def main():
    # TODO: Better CLI handling
    device = sys.argv[1] if len(sys.argv) > 1 else "/dev/co2mini0"
    logger.info("Starting with device %s", device)

    # Expose metrics
    start_http_server(config.PROMETHEUS_PORT)

    co2meter = meter.CO2Meter(device=device, callback=co2_callback)
    co2meter.start()

    dht_sensor = None

    if config.DHT_DEVICE is not None and config.DHT_PIN is not None:
        dht_sensor = dht.DHTSensor(callback=dht_callback)
        dht_sensor.start()

    try:
        from .homekit import start_homekit

        logging.info("Starting homekit")
        start_homekit(co2meter, dht_sensor)
    except ImportError:
        pass

    # Ensure thread doesn't just end without cleanup
    co2meter.join()
    if dht_sensor is not None:
        dht_sensor.join()


if __name__ == "__main__":
    main()
