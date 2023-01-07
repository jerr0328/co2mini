import os

PROMETHEUS_PORT = int(os.getenv("CO2_PROMETHEUS_PORT", 9999))
PROMETHEUS_NAMESPACE = os.getenv("CO2_PROMETHEUS_NAMESPACE", "")

# DHT Device setup (DHT11, DHT22, or None for no extra temperature/humidity sensor)
DHT_DEVICE = os.getenv("CO2_DHT_DEVICE")
DHT_PIN = os.getenv("CO2_DHT_PIN")
