"""Elite 200 V2 fields."""

from ..base_devices.ProtocolV2Device import ProtocolV2Device


class Elite200V2(ProtocolV2Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "Elite200V2", sn)
