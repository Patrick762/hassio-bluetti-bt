"""Device builder functions."""

import re

from ..devices.ac60 import AC60
from ..devices.ac70 import AC70
from ..devices.ac70p import AC70P
from ..devices.ac180 import AC180
from ..devices.ac180p import AC180P
from ..devices.ac200l import AC200L
from ..devices.ac200m import AC200M
from ..devices.ac300 import AC300
from ..devices.ac500 import AC500
from ..devices.eb3a import EB3A
from ..devices.ep500 import EP500
from ..devices.ep500p import EP500P
from ..devices.ep600 import EP600
from ..devices.ep760 import EP760
from ..devices.ep800 import EP800
from ..devices.elite100v2 import Elite100V2

DEVICE_NAME_RE = re.compile(
    r"^(AC60|AC70|AC70P|AC180|AC180P|AC200L|AC200M|AC300|AC500|EB3A|EP500|EP500P|EP600|EP760|EP800|EL100V2)(\d+)$"
)


def build_device(address: str, name: str):
    match = DEVICE_NAME_RE.match(name)
    if match[1] == "AC60":
        return AC60(address, match[2])
    if match[1] == "AC70":
        return AC70(address, match[2])
    if match[1] == "AC70P":
        return AC70P(address, match[2])
    if match[1] == "AC180":
        return AC180(address, match[2])
    if match[1] == "AC180P":
        return AC180P(address, match[2])
    if match[1] == "AC200L":
        return AC200L(address, match[2])
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
    if match[1] == "EL100V2":
        return Elite100V2(address, match[2])


def get_type_by_bt_name(bt_name: str):
    match = DEVICE_NAME_RE.match(bt_name)
    if match is None:
        return "Unknown"
    return match[1]
