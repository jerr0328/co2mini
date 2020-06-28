"""
Module for reading out CO2Meter USB devices
Code adapted from Michael Heinemann under MIT License: https://github.com/heinemml/CO2Meter
"""
import fcntl
import logging
import threading

CO2METER_CO2 = 0x50
CO2METER_TEMP = 0x42
CO2METER_HUM = 0x41
HIDIOCSFEATURE_9 = 0xC0094806

logger = logging.getLogger(__name__)


def _convert_value(sensor, value):
    """ Apply Conversion of value dending on sensor type """
    if sensor == CO2METER_TEMP:
        return round(value / 16.0 - 273.1, 1)
    if sensor == CO2METER_HUM:
        return round(value / 100.0, 1)

    return value


def _hd(data):
    """ Helper function for printing the raw data """
    return " ".join("%02X" % e for e in data)


class CO2Meter(threading.Thread):
    _key = [0xC4, 0xC6, 0xC0, 0x92, 0x40, 0x23, 0xDC, 0x96]
    _device = ""
    _values = {}
    _file = ""
    running = True
    _callback = None

    def __init__(self, device="/dev/co2mini0", callback=None):
        super().__init__(daemon=True)
        self._device = device
        self._callback = callback
        self._file = open(device, "a+b", 0)

        set_report = [0] + self._key
        fcntl.ioctl(self._file, HIDIOCSFEATURE_9, bytearray(set_report))

    def run(self):
        while self.running:
            self._read_data()

    def _read_data(self):
        """
        Function that reads from the device, decodes it, validates the checksum
        and adds the data to the dict _values.
        Additionally calls the _callback if set
        """
        try:
            data = list(self._file.read(8))
            decrypted = self._decrypt(data)
            if decrypted[4] != 0x0D or (sum(decrypted[:3]) & 0xFF) != decrypted[3]:
                logger.error("Checksum error: %s => %s", _hd(data), _hd(decrypted))
            else:
                operation = decrypted[0]
                val = decrypted[1] << 8 | decrypted[2]
                self._values[operation] = _convert_value(operation, val)
                if self._callback is not None:
                    if operation in {CO2METER_CO2, CO2METER_TEMP} or (
                        operation == CO2METER_HUM and val != 0
                    ):
                        self._callback(sensor=operation, value=self._values[operation])
        except Exception:
            logger.exception("Exception reading data")
            self.running = False

    def _decrypt(self, data):
        """
        The received data has some weak crypto that needs to be decoded first
        """
        cstate = [0x48, 0x74, 0x65, 0x6D, 0x70, 0x39, 0x39, 0x65]
        shuffle = [2, 4, 0, 7, 1, 6, 5, 3]

        phase1 = [0] * 8
        for i, j in enumerate(shuffle):
            phase1[j] = data[i]

        phase2 = [0] * 8
        for i in range(8):
            phase2[i] = phase1[i] ^ self._key[i]

        phase3 = [0] * 8
        for i in range(8):
            phase3[i] = ((phase2[i] >> 3) | (phase2[(i - 1 + 8) % 8] << 5)) & 0xFF

        ctmp = [0] * 8
        for i in range(8):
            ctmp[i] = ((cstate[i] >> 4) | (cstate[i] << 4)) & 0xFF

        out = [0] * 8
        for i in range(8):
            out[i] = (0x100 + phase3[i] - ctmp[i]) & 0xFF

        return out

    def get_co2(self):
        """
        read the co2 value from _values
        :returns dict with value or empty
        """
        if not self.running:
            raise IOError("worker thread couldn't read data")
        result = {}
        if CO2METER_CO2 in self._values:
            result = {"co2": self._values[CO2METER_CO2]}

        return result

    def get_temperature(self):
        """
        reads the temperature from _values
        :returns dict with value or empty
        """
        if not self.running:
            raise IOError("worker thread couldn't read data")
        result = {}
        if CO2METER_TEMP in self._values:
            result = {"temperature": self._values[CO2METER_TEMP]}

        return result

    def get_humidity(self):  # not implemented by all devices
        """
        reads the humidty from _values.
        not all devices support this but might still return a value 0.
        So values of 0 are discarded.
        :returns dict with value or empty
        """
        if not self.running:
            raise IOError("worker thread couldn't read data")
        result = {}
        if CO2METER_HUM in self._values and self._values[CO2METER_HUM] != 0:
            result = {"humidity": self._values[CO2METER_HUM]}
        return result

    def get_data(self):
        """
        get all currently available values
        :returns dict with value or empty
        """
        result = {}
        result.update(self.get_co2())
        result.update(self.get_temperature())
        result.update(self.get_humidity())

        return result
