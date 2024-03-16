"""EP760 fields."""

from ..base_devices.ProtocolV2Device import ProtocolV2Device


class EP760(ProtocolV2Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "EP760", sn)
