import json
import logging

import paho.mqtt.client as mqtt

from . import config

logger = logging.getLogger(__name__)
HA_STATUS_TOPIC = f"{config.MQTT_DISCOVERY_PREFIX}/status"
HA_PREFIX = (
    f"{config.MQTT_DISCOVERY_PREFIX}/sensor/{config.HOSTNAME}/{config.MQTT_OBJECT_ID}"
)
HA_TEMP_PREFIX = f"{HA_PREFIX}_temp"
HA_CO2_PREFIX = f"{HA_PREFIX}_co2"
EXPIRE_AFTER_SECONDS = 600


def send_discovery_message(client: mqtt.Client):
    logger.info("Sending discovery message to mqtt")
    device = {"identifiers": [config.HOSTNAME], "name": config.NAME}
    temp_config = {
        "device_class": "temperature",
        "expire_after": EXPIRE_AFTER_SECONDS,
        "icon": "mdi:temperature-celsius",
        "state_topic": f"{HA_TEMP_PREFIX}/state",
        "unit_of_measurement": "°C",
        "unique_id": f"{config.MQTT_OBJECT_ID}_T",
        "device": device,
    }
    co2_config = {
        "device_class": "carbon_dioxide",
        "expire_after": EXPIRE_AFTER_SECONDS,
        "icon": "mdi:periodic-table-co2",
        "state_topic": f"{HA_CO2_PREFIX}/state",
        "unit_of_measurement": "ppm",
        "unique_id": f"{config.MQTT_OBJECT_ID}_CO2",
        "device": device,
    }
    client.publish(f"{HA_TEMP_PREFIX}/config", json.dumps(temp_config))
    client.publish(f"{HA_CO2_PREFIX}/config", json.dumps(co2_config))


def on_connect(client: mqtt.Client, *args, **kwargs):
    send_discovery_message(client)
    client.subscribe(HA_STATUS_TOPIC, qos=1)


def handle_homeassistant_status(client: mqtt.Client, userdata, msg):
    if msg.payload == "online":
        send_discovery_message(client)


def get_mqtt_client() -> mqtt.Client:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.message_callback_add(
        f"{config.MQTT_DISCOVERY_PREFIX}/status", handle_homeassistant_status
    )
    if config.MQTT_USERNAME:
        client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD or None)
    return client


def send_co2_value(client: mqtt.Client, value: float):
    client.publish(f"{HA_CO2_PREFIX}/state", value, retain=True)


def send_temp_value(client: mqtt.Client, value: float):
    client.publish(f"{HA_TEMP_PREFIX}/state", value, retain=True)


def start_client(client: mqtt.Client):
    """Blocking call to connect to the MQTT broker and loop forever"""
    logger.info(f"Connecting to {config.MQTT_BROKER}")
    client.connect(config.MQTT_BROKER)
    client.loop_forever(timeout=1.0, max_packets=1, retry_first_connection=False)
    logger.error("MQTT Failure")
