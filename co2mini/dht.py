import logging
import threading
import time
from typing import Optional

from . import config

logger = logging.getLogger(__name__)

if config.DHT_DEVICE:
    import adafruit_dht
    import board

    DHT = getattr(adafruit_dht, config.DHT_DEVICE, None)
    PIN = getattr(board, config.DHT_PIN, None)
else:
    DHT = None
    PIN = None


class DHTSensor(threading.Thread):
    running = True

    def __init__(self, callback=None):
        super().__init__(daemon=True)
        self._callback = callback
        self.last_results = {}
        if DHT is not None and PIN is not None:
            self.DHT = DHT(PIN)
        else:
            self.DHT = None
            self.running = False

    def run(self):
        while self.running:
            results = self.get_data()
            self.last_results.update(results)
            if self._callback is not None:
                self._callback(results)
            time.sleep(2)

    def get_temperature(self) -> Optional[float]:
        try:
            return self.DHT.temperature
        except RuntimeError:
            logger.exception("Failed to fetch temperature data from DHT")
            return None

    def get_humidity(self) -> Optional[float]:
        try:
            return self.DHT.humidity
        except RuntimeError:
            logger.exception("Failed to fetch humidity data from DHT")
            return None

    def get_data(self) -> dict:
        result = {}
        temperature = self.get_temperature()
        if temperature is not None:
            result["temperature"] = temperature
        humidity = self.get_humidity()
        if humidity is not None:
            result["humidity"] = humidity
        return result
