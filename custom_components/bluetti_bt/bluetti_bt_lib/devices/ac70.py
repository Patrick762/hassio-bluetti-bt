"""AC70 fields."""

from typing import List

from ..utils.commands import ReadHoldingRegisters
from ..base_devices.ProtocolV2Device import ProtocolV2Device


class AC70(ProtocolV2Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "AC70", sn, use_additional_fields=True)
