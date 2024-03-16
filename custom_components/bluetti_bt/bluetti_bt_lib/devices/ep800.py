"""EP800 fields."""

from ..base_devices.ProtocolV2Device import ProtocolV2Device


class EP800(ProtocolV2Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "EP800", sn)
