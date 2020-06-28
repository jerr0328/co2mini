#!/usr/bin/env python3

import logging
import os
import sys

from prometheus_client import Gauge, start_http_server

from . import meter

co2_gauge = Gauge("co2", "CO2 levels in PPM")
temp_gauge = Gauge("temperature", "Temperature in C")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
PROMETHEUS_PORT = os.getenv("CO2_PROMETHEUS_PORT", 9999)


def co2_callback(sensor, value):
    if sensor == meter.CO2METER_CO2:
        co2_gauge.set(value)
    elif sensor == meter.CO2METER_TEMP:
        temp_gauge.set(value)


def main():
    device = sys.argv[1] or "/dev/co2mini0"
    logger.info("Starting with device %s", device)

    # Expose metrics
    start_http_server(PROMETHEUS_PORT)

    co2meter = meter.CO2Meter(device=device, callback=co2_callback)
    co2meter.start()

    try:
        from .homekit import start_homekit

        logging.info("Starting homekit")
        start_homekit(co2meter)
    except ImportError:
        pass


if __name__ == "__main__":
    main()
