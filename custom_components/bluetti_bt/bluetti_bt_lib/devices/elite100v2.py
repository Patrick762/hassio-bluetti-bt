"""Elite 100 V2 fields."""

from ..base_devices.ProtocolV2Device import ProtocolV2Device


class Elite100V2(ProtocolV2Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "Elite100V2", sn)
