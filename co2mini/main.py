#!/usr/bin/env python3

import logging
import sys
from functools import partial

from prometheus_client import Gauge, start_http_server

from . import config, meter

try:
    from . import mqtt
except ImportError:

    class mqtt:
        @staticmethod
        def send_co2_value(*args, **kwargs):
            pass

        @staticmethod
        def send_temp_value(*args, **kwargs):
            pass

        @staticmethod
        def get_mqtt_client():
            pass

        @staticmethod
        def start_client(*args, **kwargs):
            pass


co2_gauge = Gauge("co2", "CO2 levels in PPM")
temp_gauge = Gauge("temperature", "Temperature in C")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def co2_callback(sensor, value):
    if sensor == meter.CO2METER_CO2:
        co2_gauge.set(value)
    elif sensor == meter.CO2METER_TEMP:
        temp_gauge.set(value)


def generate_callback(mqtt_client):
    # TODO: Create the callback, support the loop
    co2_handlers = [co2_gauge.set]
    temp_handlers = [temp_gauge.set]
    if mqtt_client:
        co2_handlers.append(partial(mqtt.send_co2_value, mqtt_client))
        temp_handlers.append(partial(mqtt.send_temp_value, mqtt_client))

    def co2_callback(sensor, value):
        if sensor == meter.CO2METER_CO2:
            for handler in co2_handlers:
                handler(value)
        elif sensor == meter.CO2METER_TEMP:
            for handler in temp_handlers:
                handler(value)

    return co2_callback


def main():
    # TODO: Better CLI handling
    device = sys.argv[1] if len(sys.argv) > 1 else "/dev/co2mini0"
    logger.info("Starting with device %s", device)

    # Expose metrics
    start_http_server(config.PROMETHEUS_PORT)

    mqtt_client = mqtt.get_mqtt_client() if config.MQTT_ENABLED else None

    co2meter = meter.CO2Meter(device=device, callback=generate_callback(mqtt_client))
    co2meter.start()

    try:
        from .homekit import start_homekit

        logging.info("Starting homekit")
        start_homekit(co2meter)
    except ImportError:
        pass

    if mqtt_client:
        mqtt.start_client(mqtt_client)

    # Ensure thread doesn't just end without cleanup
    co2meter.join()


if __name__ == "__main__":
    main()
