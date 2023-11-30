import platform

from environs import Env

env = Env()
env.read_env()

HOSTNAME = platform.node()

PROMETHEUS_PORT: int = env.int("CO2_PROMETHEUS_PORT", 9999)
NAME: str = env.str("CO2MINI_NAME", "co2mini")

with env.prefixed("MQTT_"):
    MQTT_ENABLED: bool = env.bool("ENABLED", False)
    MQTT_BROKER: str = env.str("BROKER", "localhost")
    MQTT_PORT: str = env.int("PORT", 1883)
    MQTT_USERNAME: str = env.str("USERNAME", "")
    MQTT_PASSWORD: str = env.str("PASSWORD", "")
    MQTT_DISCOVERY_PREFIX: str = env.str("DISCOVERY_PREFIX", "homeassistant")
    MQTT_RETAIN_DISCOVERY: bool = env.bool("RETAIN_DISCOVERY", False)
    # Object ID needs to be unique
    MQTT_OBJECT_ID: str = env.str("OBJECT_ID", f"co2mini_{HOSTNAME}")
