"""Tools."""

import re


def mac_loggable(mac: str) -> str:
    """Remove parts of the mac address for logging."""
    splitted = mac.split(":")
    return "XX:XX:XX:XX:XX:" + splitted[-1]


def unique_id_logable(unique_id: str) -> str:
    """Remove parts of the unique id for logging."""
    splitted = unique_id.split("_", maxsplit=1)
    serial = splitted[0][:6]
    return serial + "XXXXXXXXXX" + splitted[1]


def sanitize_device_name(name: str) -> str:
    """Remove invalid characters from the device name.

    Spaces and lowercase letters are kept because some device types contain them
    (e.g. "Handsfree 2") and the name is later passed to build_device.
    """
    return re.sub("[^A-Za-z0-9 ]+", "", name).strip()
