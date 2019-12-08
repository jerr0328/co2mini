# CO2 monitoring with Prometheus

This reads from the CO2 Meter and makes it available as a Prometheus service.
The core logic comes from [this hackaday article](https://hackaday.io/project/5301-reverse-engineering-a-low-cost-usb-co-monitor/log/17909-all-your-base-are-belong-to-us).

## Setup

1. Install Python 3
2. Install python3-prometheus-client
3. Set up CO2 udev rules by copying `90-co2mini.rules` to `/etc/udev/rules.d/90-co2mini.rules`
4. Set up the service by copying `co2_prometheus.service` to `/lib/systemd/system/co2_prometheus.service`
5. Run `systemctl enable co2_prometheus.service`
