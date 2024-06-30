"""AC180P fields."""

from typing import List
from enum import Enum, unique

from ..utils.commands import ReadHoldingRegisters
from ..base_devices.ProtocolV2Device import ProtocolV2Device

@unique
class ChargingMode(Enum):
    STANDARD = 0
    SILENT = 1
    TURBO = 2

class AC180P(ProtocolV2Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "AC180P", sn)

        # Power IO
        self.struct.add_uint_field('dc_output_power', 140)
        self.struct.add_uint_field('ac_output_power', 142)
        self.struct.add_uint_field('dc_input_power', 144)
        self.struct.add_uint_field('ac_input_power', 146)

        # Input Details (1100 - 1300)
        self.struct.add_decimal_field('ac_input_voltage', 1314, 1)

        # Controls (2000)
        self.struct.add_bool_field('ac_output_on', 2011)
        self.struct.add_bool_field('dc_output_on', 2012)
        self.struct.add_enum_field('charging_mode', 2020, ChargingMode)
        self.struct.add_bool_field('power_lifting_on', 2021)

        # Controls (2200)
        self.struct.add_bool_field('grid_enhancement_mode_on', 2225)

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        return super().polling_commands + [
            ReadHoldingRegisters(140, 1),
            ReadHoldingRegisters(142, 1),
            ReadHoldingRegisters(144, 1),
            ReadHoldingRegisters(146, 1),
            ReadHoldingRegisters(1314, 1),
            ReadHoldingRegisters(2011, 1),
            ReadHoldingRegisters(2012, 1),
            ReadHoldingRegisters(2020, 1),
            ReadHoldingRegisters(2021, 1),
        ]

    @property
    def writable_ranges(self) -> List[range]:
        return super().writable_ranges + [
            range(2000, 2022),
            range(2200, 2226)
        ]