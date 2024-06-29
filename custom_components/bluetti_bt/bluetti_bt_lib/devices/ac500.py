"""AC500 fields."""

from typing import List

from ..utils.commands import ReadHoldingRegisters
from ..field_enums import AutoSleepMode, OutputMode, SplitPhaseMachineType, UpsMode
from ..base_devices.ProtocolV1Device import ProtocolV1Device


class AC500(ProtocolV1Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "AC500", sn)

        # Details
        self.struct.add_enum_field("ac_output_mode", 70, OutputMode)
        self.struct.add_decimal_field("internal_ac_voltage", 71, 1)
        self.struct.add_decimal_field("internal_current_one", 72, 1)
        self.struct.add_int_field("internal_power_one", 73)
        self.struct.add_decimal_field("internal_ac_frequency", 74, 2)
        self.struct.add_decimal_field("internal_current_two", 75, 1)
        self.struct.add_int_field("internal_power_two", 76)
        self.struct.add_decimal_field("ac_input_voltage", 77, 1)
        self.struct.add_decimal_field("internal_current_three", 78, 1, (0, 100))
        self.struct.add_int_field("internal_power_three", 79)
        self.struct.add_decimal_field("ac_input_frequency", 80, 2)
        self.struct.add_uint_field("pv_input_voltage1", 86, multiplier=.1)
        self.struct.add_decimal_field("pv_input_power1", 87, 1, multiplier=10)
        self.struct.add_decimal_field("pv_input_current1", 88, 2, multiplier=10)

        # Battery packs
        self.struct.add_uint_field("pack_num_max", 91)  # internal
        self.struct.add_decimal_field("total_battery_voltage", 92, 1)
        self.struct.add_uint_field("pack_num_result", 96)  # internal
        self.struct.add_decimal_field("pack_voltage", 98, 2)  # Full pack voltage
        self.struct.add_uint_field("pack_battery_percent", 99)
        self.struct.add_decimal_array_field("cell_voltages", 105, 16, 2)  # internal
        self.struct.add_version_field('pack_bms_version', 201)

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
    def pack_num_max(self):
        return 6

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        return self.struct.get_read_holding_registers(
            filter=lambda address: address <= 90 or address >= 256 # pack_polling_commands
        )

    @property
    def writable_ranges(self) -> List[range]:
        return super().writable_ranges + [
            range(3001, 3017),
            range(3061, 3062),
        ]

    @property
    def pack_polling_commands(self) -> List[ReadHoldingRegisters]:
        return [
            ReadHoldingRegisters(91, 37),
            ReadHoldingRegisters(201, 2),
        ]
