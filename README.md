# CO2 monitoring with Prometheus

This reads from the CO2 Meter and makes it available as a Prometheus service.
The core logic comes from [this hackaday article](https://hackaday.io/project/5301-reverse-engineering-a-low-cost-usb-co-monitor/log/17909-all-your-base-are-belong-to-us).

## Setup

Note this assumes you are running on a Raspberry Pi running Raspberry Pi OS (Bullseye)

1. Install Python 3
2. Install the monitor with `python3 -m pip install co2mini[homekit]` (remove `[homekit]` if you don't use HomeKit)
3. Set up CO2 udev rules by copying `90-co2mini.rules` to `/etc/udev/rules.d/90-co2mini.rules`
4. Set up the service by copying `co2mini.service` to `/etc/systemd/system/co2mini.service`
5. (Optional) Put a configuration file (see Configuration section below) in `/etc/co2mini.env`
6. Run `systemctl enable co2mini.service`

## Configuration

The `/etc/co2mini.env` file contains the environment variables used to configure co2mini beyond the defaults.
This is mostly necessary when enabling MQTT.

Example:

```bash
MQTT_ENABLED=true
MQTT_BROKER=localhost
```

### MQTT/Home Assistant

The MQTT feature is meant to work with Home Assistant, although nothing bad will happen if you just want to use the MQTT messages directly.

When co2mini starts up, it will send out the discovery message that Home Assistant expects, as well as responding to homeassistant's status when coming online.
Be sure those are enabled in the Home Assistant MQTT integration (usually is enabled by default) if you have any issues.

To configure co2mini, the following environment variables are available:

Variable                | Default              | Description
------------------------|----------------------|---------------------------------------------------------------------------------------------------------
`NAME`                  | `co2mini`            | This is used for the default display name of the device in Home Assistant
`MQTT_ENABLED`          | `False`              | Used to enable/disable sending information over MQTT
`MQTT_BROKER`           | `localhost`          | MQTT Broker hostname
`MQTT_PORT`             | `1883`               | MQTT broker port number (1883 is the standard MQTT broker port)
`MQTT_USERNAME`         |                      | Username for authenticating to MQTT broker (leave blank if no authentication is needed)
`MQTT_PASSWORD`         |                      | Password for authenticating to MQTT broker (leave blank if no authentication is needed)
`MQTT_DISCOVERY_PREFIX` | `homeassistant`      | Prefix for sending MQTT discovery and state messages.
`MQTT_RETAIN_DISCOVERY` | `False`              | Flag to enable setting `retain=True` on the discovery messages. You probably don't need this.
`MQTT_OBJECT_ID`        | `co2mini_{HOSTNAME}` | Override for setting the `object_id` in Home Assistant. Default builds using the hostname of the device.

### Homekit

If you have the `homekit` dependencies installed, on the first startup you will need to check the logs to get the setup code to integrate with Homekit.
You can find the code using `journalctl -u co2mini.service` or possibly by checking the status with `systemctl status co2mini.service`.

Note also that it's sometimes possible that co2mini will have some errors logged and won't be reporting in Homekit anymore.
If this happens, it seems like the easiest thing to do is to remove the device from your homekit, remove the `accessory.state` file in your home (`rm accessory.state`) and restart `co2mini` (`sudo systemctl restart co2mini.service`) to get a new code to pair.

## Special notes for Dietpi users

- Be sure to install `Python3 pip` as well (ID `130`)
- Make sure the dietpi user is in `plugdev` group (`sudo usermod -aG plugdev dietpi`)
