"""Device builder functions."""

import re

from ..devices.ac60 import AC60
from ..devices.ac200m import AC200M
from ..devices.ac300 import AC300
from ..devices.ac500 import AC500
from ..devices.eb3a import EB3A
from ..devices.ep500 import EP500
from ..devices.ep500p import EP500P
from ..devices.ep600 import EP600
from ..devices.ep760 import EP760
from ..devices.ep800 import EP800

DEVICE_NAME_RE = re.compile(
    r"^(AC60|AC200M|AC300|AC500|EB3A|EP500|EP500P|EP600|EP760|EP800)(\d+)$"
)


def build_device(address: str, name: str):
    match = DEVICE_NAME_RE.match(name)
    if match[1] == "AC60":
        return AC60(address, match[2])
    if match[1] == "AC200M":
        return AC200M(address, match[2])
    if match[1] == "AC300":
        return AC300(address, match[2])
    if match[1] == "AC500":
        return AC500(address, match[2])
    if match[1] == "EB3A":
        return EB3A(address, match[2])
    if match[1] == "EP500":
        return EP500(address, match[2])
    if match[1] == "EP500P":
        return EP500P(address, match[2])
    if match[1] == "EP600":
        return EP600(address, match[2])
    if match[1] == "EP760":
        return EP760(address, match[2])
    if match[1] == "EP800":
        return EP800(address, match[2])


def get_type_by_bt_name(bt_name: str):
    match = DEVICE_NAME_RE.match(bt_name)
    if match is None or len(match) < 2:
        return "Unknown"
    return match[1]
