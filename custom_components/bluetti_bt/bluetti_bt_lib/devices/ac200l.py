"""AC200L fields."""

from typing import List

from ..utils.commands import ReadHoldingRegisters
from ..field_enums import AutoSleepMode, OutputMode
from ..base_devices.ProtocolV1Device import ProtocolV1Device


class AC200L(ProtocolV1Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "AC200L", sn)

        # Details
        self.struct.add_enum_field("ac_output_mode", 70, OutputMode)
        self.struct.add_decimal_field("internal_ac_voltage", 71, 1, multiplier=10)
        self.struct.add_decimal_field("internal_current_one", 72, 1)
        self.struct.add_uint_field("internal_power_one", 73)
        self.struct.add_decimal_field("internal_ac_frequency", 74, 2, multiplier=10)
        self.struct.add_uint_field("internal_dc_input_voltage", 86, multiplier=.1)
        self.struct.add_decimal_field("internal_dc_input_power", 87, 1, multiplier=10)
        self.struct.add_decimal_field("internal_dc_input_current", 88, 2)

        # Battery packs
        self.struct.add_uint_field("pack_num_max", 91)  # internal
        self.struct.add_decimal_field("total_battery_voltage", 92, 1, multiplier=.1)
        self.struct.add_uint_field("pack_num_result", 96)  # internal
        self.struct.add_decimal_field("pack_voltage", 98, 2)  # Full pack voltage
        self.struct.add_uint_field("pack_battery_percent", 99)
        self.struct.add_decimal_array_field("cell_voltages", 105, 16, 2)  # internal

        # Controls
        self.struct.add_bool_field("power_off", 3060)
        self.struct.add_enum_field("auto_sleep_mode", 3061, AutoSleepMode)

    @property
    def pack_num_max(self):
        return 3

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        return super().polling_commands + [
            ReadHoldingRegisters(70, 5),
            ReadHoldingRegisters(86, 3),
            ReadHoldingRegisters(92, 1),
            ReadHoldingRegisters(3060, 2),
        ]

    @property
    def writable_ranges(self) -> List[range]:
        return super().writable_ranges + [range(3060, 3062)]

    @property
    def pack_polling_commands(self) -> List[ReadHoldingRegisters]:
        return [
            ReadHoldingRegisters(91, 2),
            ReadHoldingRegisters(96, 1),
            ReadHoldingRegisters(98, 2),
            ReadHoldingRegisters(105, 16)
        ]
