"""AC70P fields."""

from ..base_devices.ProtocolV2Device import ProtocolV2Device


class AC70P(ProtocolV2Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "AC70P", sn)
