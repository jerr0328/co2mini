import signal
from typing import Optional

from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_SENSOR

from . import dht

# PPM at which to trigger alert
CO2_ALERT_THRESHOLD = 1200
# PPM at which to clear alert (set lower to avoid flapping alerts)
CO2_ALERT_CLEAR_THRESHOLD = 1100
# Seconds between updates to homekit
UPDATE_INTERVAL_SECONDS = 60


class CO2Sensor(Accessory):
    """CO2 HomeKit Sensor"""

    category = CATEGORY_SENSOR

    def __init__(self, co2meter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.co2meter = co2meter
        self.alert = False

        serv_temp = self.add_preload_service("TemperatureSensor")
        serv_co2 = self.add_preload_service(
            "CarbonDioxideSensor", chars=["CarbonDioxideLevel"]
        )
        self.char_temp = serv_temp.configure_char("CurrentTemperature")
        self.char_co2_detected = serv_co2.configure_char("CarbonDioxideDetected")
        self.char_co2 = serv_co2.configure_char("CarbonDioxideLevel")

    @Accessory.run_at_interval(UPDATE_INTERVAL_SECONDS)
    async def run(self):
        values = self.co2meter.get_data()
        if "temperature" in values:
            self.char_temp.set_value(values["temperature"])
        if "co2" in values:
            self.char_co2.set_value(values["co2"])
            threshold = CO2_ALERT_CLEAR_THRESHOLD if self.alert else CO2_ALERT_THRESHOLD
            self.alert = values["co2"] >= threshold
            self.char_co2_detected.set_value(1 if self.alert else 0)

    async def stop(self):
        self.co2meter.running = False


class DHTSensor(Accessory):
    """DHT HomeKit Sensor"""

    category = CATEGORY_SENSOR

    def __init__(self, dht_sensor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dht_sensor = dht_sensor

        serv_temp = self.add_preload_service("TemperatureSensor")
        serv_hum = self.add_preload_service("HumiditySensor")
        self.char_temp = serv_temp.configure_char("CurrentTemperature")
        self.char_hum = serv_hum.configure_char("CurrentRelativeHumidity")

    @Accessory.run_at_interval(UPDATE_INTERVAL_SECONDS)
    async def run(self):
        values = self.dht_sensor.get_data()
        if "temperature" in values:
            self.char_temp.set_value(values["temperature"])
        if "humidity" in values:
            self.char_hum.set_value(values["humidity"])

    async def stop(self):
        self.dht_sensor.running = False


def start_homekit(co2meter, dht_sensor: Optional[dht.DHT] = None):
    # Start the accessory on port 51826
    driver = AccessoryDriver(port=51826)

    driver.add_accessory(
        accessory=CO2Sensor(co2meter=co2meter, driver=driver, display_name="CO2 Sensor")
    )
    if dht_sensor is not None:
        driver.add_accessory(
            accessory=DHTSensor(
                dht_sensor=dht_sensor, driver=driver, display_name="DHT Sensor"
            )
        )

    # We want SIGTERM (terminate) to be handled by the driver itself,
    # so that it can gracefully stop the accessory, server and advertising.
    signal.signal(signal.SIGTERM, driver.signal_handler)

    # Start it!
    driver.start()
