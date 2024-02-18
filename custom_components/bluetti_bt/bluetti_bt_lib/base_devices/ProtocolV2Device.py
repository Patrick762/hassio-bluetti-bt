"""Base device definition for V2 Protocol devices."""

from typing import List

from ..utils.commands import ReadHoldingRegisters
from ..utils.struct import DeviceStruct
from .BluettiDevice import BluettiDevice


class ProtocolV2Device(BluettiDevice):
    def __init__(self, address: str, type: str, sn: str):
        self.struct = DeviceStruct()

        # Device info
        self.struct.add_swap_string_field("device_type", 110, 6)
        self.struct.add_sn_field("serial_number", 116)

        # Power IO
        # self.struct.add_uint_field('dc_input_power', ?)
        # self.struct.add_uint_field('ac_input_power', ?)
        # self.struct.add_uint_field('ac_output_power', ?)
        # self.struct.add_uint_field('dc_output_power', ?)

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

        # Output controls
        # self.struct.add_bool_field('ac_output_on_switch', ?)
        # self.struct.add_bool_field('dc_output_on_switch', ?)

        # Add battery fields here?

        super().__init__(address, type, sn)

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        return [
            ReadHoldingRegisters(110, 6),
            ReadHoldingRegisters(116, 4),
            ReadHoldingRegisters(154, 1),
            ReadHoldingRegisters(102, 1),
        ]

    @property
    def writable_ranges(self) -> List[range]:
        return []

    @property
    def pack_polling_commands(self) -> List[ReadHoldingRegisters]:
        return []
