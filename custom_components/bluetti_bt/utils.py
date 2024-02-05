"""Tools."""

from bluetti_mqtt.bluetooth import build_device as orig_build_device

from .const import DEVICE_NAME_RE
from .devices.ep600 import EP600
from .devices.ep760 import EP760

def mac_loggable(mac: str) -> str:
    """Remove parts of the mac address for logging."""
    splitted = mac.split(":")
    return "XX:XX:XX:XX:XX:" + splitted[-1]

def unique_id_loggable(unique_id: str) -> str:
    """Remove parts of the unique id for logging."""
    splitted = unique_id.split("_", maxsplit=1)
    serial = splitted[0][:6]
    return serial + "XXXXXXXXXX" + splitted[1]

def build_device(address: str, name: str):
    match = DEVICE_NAME_RE.match(name)
    if match[1] == 'EP760':
        return EP760(address, match[2])
    elif match[1] == 'EP600':
        return EP600(address, match[2])
    else:
        return orig_build_device(address, name)
