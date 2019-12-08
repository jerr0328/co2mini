#!/usr/bin/env python3

import fcntl
import logging
import os
import sys

from prometheus_client import Counter, Gauge, start_http_server

co2_gauge = Gauge("co2", "CO2 levels in PPM")
temp_gauge = Gauge("temperature", "Temperature in C")
checksum_error_counter = Counter("checksum_errors", "Number of checksum errors seen")

logger = logging.getLogger(__name__)
PROMETHEUS_PORT = os.getenv("CO2_PROMETHEUS_PORT", 9999)

# From http://co2meters.com/Documentation/AppNotes/AN146-RAD-0401-serial-communication.pdf
OP_CO2 = 0x50
OP_TEMP = 0x42


def decrypt(key, data):
    # Magic from https://hackaday.io/project/5301-reverse-engineering-a-low-cost-usb-co-monitor/log/17909-all-your-base-are-belong-to-us
    cstate = [0x48, 0x74, 0x65, 0x6D, 0x70, 0x39, 0x39, 0x65]
    shuffle = [2, 4, 0, 7, 1, 6, 5, 3]

    phase1 = [0] * 8
    for i, o in enumerate(shuffle):
        phase1[o] = data[i]

    phase2 = [0] * 8
    for i in range(8):
        phase2[i] = phase1[i] ^ key[i]

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


def hd(d):
    return " ".join("%02X" % e for e in d)


if __name__ == "__main__":
    # Key retrieved from /dev/random, guaranteed to be random ;)
    key = [0xC4, 0xC6, 0xC0, 0x92, 0x40, 0x23, 0xDC, 0x96]

    fp = open(sys.argv[1], "a+b", 0)

    HIDIOCSFEATURE_9 = 0xC0094806
    set_report = [0] + key
    fcntl.ioctl(fp, HIDIOCSFEATURE_9, bytearray(set_report))

    values = {}

    # Expose metrics
    start_http_server(PROMETHEUS_PORT)

    while True:
        data = list(fp.read(8))
        decrypted = decrypt(key, data)
        if decrypted[4] != 0x0D or (sum(decrypted[:3]) & 0xFF) != decrypted[3]:
            logger.warning("Checksum error: %s => %s", hd(data), hd(decrypted))
            checksum_error_counter.inc()
        else:
            op = decrypted[0]
            val = decrypted[1] << 8 | decrypted[2]

            if op == OP_CO2:
                co2_gauge.set(val)
            if op == OP_TEMP:
                temp_gauge.set(val / 16.0 - 273.15)
