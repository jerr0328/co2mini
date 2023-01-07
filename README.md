# CO2 monitoring with Prometheus

This reads from the CO2 Meter and makes it available as a Prometheus service.
The core logic comes from [this hackaday article](https://hackaday.io/project/5301-reverse-engineering-a-low-cost-usb-co-monitor/log/17909-all-your-base-are-belong-to-us).

## Setup

Note this assumes you are running on a Raspberry Pi running Raspberry Pi OS (Buster)

1. Install Python 3 (`sudo apt-get install python3`).
2. Install the monitor with `python3 -m pip install co2mini[homekit]` (remove `[homekit]` if you don't use HomeKit)
3. Set up CO2 udev rules by copying `90-co2mini.rules` to `/etc/udev/rules.d/90-co2mini.rules`
4. Set up the service by copying `co2mini.service` to `/etc/systemd/system/co2mini.service`
5. Run `systemctl enable co2mini.service`

## DHT Sensor support

If you have an additional DHT11/DHT22 sensor on your device, the monitor can also support reporting from that sensor.
The only additional system dependency is for libgpiod2 (`sudo apt-get install libgpiod2`), and has been tested on a Raspberry Pi 4 with a DHT22 sensor.
You can then set the environment variables (e.g. in the `co2mini.service` file):

- `CO2_DHT_DEVICE`: either `DHT11` or `DHT22`
- `CO2_DHT_PIN`: The corresponding pin, see the [CircuitPython documentation](https://learn.adafruit.com/arduino-to-circuitpython/the-board-module) for more information on what to set this to. Example for GPIO4 (pin 7) on a Raspberry Pi, you should set this to `D4`.

If the variables are not set, then the DHT sensor is not used. Note that not every refresh of the sensor works, information would be available in the logs to further debug.
