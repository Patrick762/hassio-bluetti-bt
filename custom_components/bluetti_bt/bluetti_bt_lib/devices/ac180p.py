"""AC180P fields."""

from typing import List

from ..utils.commands import ReadHoldingRegisters
from ..base_devices.ProtocolV2Device import ProtocolV2Device


class AC180P(ProtocolV2Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "AC180P", sn, use_additional_fields=True)
