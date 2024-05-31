"""EP500 fields."""

from typing import List

from ..utils.commands import ReadHoldingRegisters
from ..field_enums import AutoSleepMode, OutputMode, SplitPhaseMachineType, UpsMode
from ..base_devices.ProtocolV1Device import ProtocolV1Device


class EP500(ProtocolV1Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "EP500", sn)

        # Details
        self.struct.add_enum_field("ac_output_mode", 70, OutputMode)
        self.struct.add_decimal_field("internal_ac_voltage", 71, 1)
        self.struct.add_decimal_field("internal_current_one", 72, 1)
        self.struct.add_uint_field("internal_power_one", 73)
        self.struct.add_decimal_field("internal_ac_frequency", 74, 2)
        self.struct.add_decimal_field("internal_current_two", 75, 1)
        self.struct.add_uint_field("internal_power_two", 76)
        self.struct.add_decimal_field("ac_input_voltage", 77, 1)
        self.struct.add_decimal_field("internal_current_three", 78, 1, (0, 100))
        self.struct.add_uint_field("internal_power_three", 79)
        self.struct.add_decimal_field("ac_input_frequency", 80, 2)
        self.struct.add_uint_field("internal_dc_input_voltage", 86)
        self.struct.add_decimal_field("internal_dc_input_power", 87, 1)
        self.struct.add_decimal_field("internal_dc_input_current", 88, 2)

        # Battery packs
        self.struct.add_uint_field("pack_num_max", 91)  # internal
        self.struct.add_decimal_field("total_battery_voltage", 92, 1)
        self.struct.add_uint_field("pack_num_result", 96)  # internal
        self.struct.add_decimal_field("pack_voltage", 98, 2)  # Full pack voltage
        self.struct.add_uint_field("pack_battery_percent", 99)
        self.struct.add_decimal_array_field("cell_voltages", 105, 16, 2)  # internal

        # Controls
        self.struct.add_enum_field("ups_mode", 3001, UpsMode)
        self.struct.add_bool_field("split_phase_on", 3004)
        self.struct.add_enum_field(
            "split_phase_machine_mode", 3005, SplitPhaseMachineType
        )
        self.struct.add_bool_field("grid_charge_on", 3011)
        self.struct.add_bool_field("time_control_on", 3013)
        self.struct.add_uint_field("battery_range_start", 3015)
        self.struct.add_uint_field("battery_range_end", 3016)
        self.struct.add_enum_field("auto_sleep_mode", 3061, AutoSleepMode)

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        return super().polling_commands + [
            ReadHoldingRegisters(70, 11),
            ReadHoldingRegisters(86, 3),
            ReadHoldingRegisters(92, 1),
            ReadHoldingRegisters(3001, 1),
            ReadHoldingRegisters(3004, 2),
            ReadHoldingRegisters(3011, 1),
            ReadHoldingRegisters(3013, 1),
            ReadHoldingRegisters(3015, 2),
            ReadHoldingRegisters(3061, 1),
        ]

    @property
    def writable_ranges(self) -> List[range]:
        return super().writable_ranges + [
            range(3001, 3017),
            range(3061, 3062),
        ]

    @property
    def pack_polling_commands(self) -> List[ReadHoldingRegisters]:
        return [
            ReadHoldingRegisters(91, 2),
            ReadHoldingRegisters(96, 1),
            ReadHoldingRegisters(98, 2),
            ReadHoldingRegisters(105, 16),
        ]
