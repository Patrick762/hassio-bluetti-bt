"""Base device definition for V2 Protocol devices."""

from typing import List

from ..utils.commands import ReadHoldingRegisters
from ..utils.struct import DeviceStruct
from ..field_enums import ChargingMode
from .BluettiDevice import BluettiDevice


class ProtocolV2Device(BluettiDevice):
    def __init__(self, address: str, type: str, sn: str, use_additional_fields: bool = False):
        self.use_additional_fields = use_additional_fields
        self.struct = DeviceStruct()

        # Device info
        self.struct.add_swap_string_field("device_type", 110, 6)
        self.struct.add_sn_field("serial_number", 116)

        # Power IO statistics
        self.struct.add_decimal_field(
            "power_generation", 154, 1
        )  # Total power generated since last reset (kwh)

        # Battery
        self.struct.add_uint_field("total_battery_percent", 102)

        # Battery packs
        # self.struct.add_uint_field('pack_num_max', ?) # internal
        # self.struct.add_decimal_field('total_battery_voltage', ?, 1)
        # self.struct.add_uint_field('pack_num', ?) # internal
        # self.struct.add_decimal_field('pack_voltage', ?, 2)  # Full pack voltage
        # self.struct.add_uint_field('pack_battery_percent', ?)

        # Output state
        # self.struct.add_bool_field('ac_output_on', ?)
        # self.struct.add_bool_field('dc_output_on', ?)

        # Pack selector
        # self.struct.add_uint_field('pack_num', ?) # internal

        # Add battery fields here?

        # Additional fields for AC70P, AC180P, AC70, and AC70P
        if use_additional_fields:
            # Power IO
            self.struct.add_uint_field("dc_output_power", 140)
            self.struct.add_uint_field("ac_output_power", 142)
            self.struct.add_uint_field("dc_input_power", 144)
            self.struct.add_uint_field("ac_input_power", 146)

            # Input Details (1100 - 1300)
            self.struct.add_decimal_field("ac_input_voltage", 1314, 1)

            # Controls (2000)
            self.struct.add_bool_field("ac_output_on_switch", 2011)
            self.struct.add_bool_field("dc_output_on_switch", 2012)
            self.struct.add_bool_field("silent_charging_on", 2020)
            self.struct.add_enum_field("charging_mode", 2020, ChargingMode)
            self.struct.add_bool_field("power_lifting_on", 2021)

            # Controls (2200)
            self.struct.add_bool_field("grid_enhancement_mode_on", 2225)

        super().__init__(address, type, sn)

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        default_registers = [
            (110, 6),
            (116, 4),
            (154, 1),
            (102, 1),
        ]

        additional_registers = [
            (140, 1),
            (142, 1),
            (144, 1),
            (146, 1),
            (1314, 1),
            (2011, 1),
            (2012, 1),
            (2020, 1),
            (2021, 1),
            (2225, 1)
        ]

        all_registers = default_registers
        if self.use_additional_fields:
            all_registers += additional_registers

        return [ReadHoldingRegisters(address, count) for address, count in all_registers]

    @property
    def writable_ranges(self) -> List[range]:
        writeable_ranges = []
        if self.use_additional_fields:
            writeable_ranges += [
                range(2000, 2022),
                range(2200, 2226),
            ]
        return writeable_ranges

    @property
    def pack_polling_commands(self) -> List[ReadHoldingRegisters]:
        return []
