"""AC2P fields."""

from typing import List

from ..base_devices.ProtocolV2Device import ProtocolV2Device
from ..utils.commands import ReadHoldingRegisters


class AC2P(ProtocolV2Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "AC2P", sn)

        # Core fields
        self.struct.add_uint_field('total_battery_percent', 102)
        self.struct.add_swap_string_field('device_type', 110, 6)
        self.struct.add_sn_field('serial_number', 116)
        self.struct.add_decimal_field('power_generation', 154, 1)  # Total kWh generated

        # Power stats
        self.struct.add_uint_field('dc_output_power', 140)
        self.struct.add_uint_field('ac_output_power', 142)
        self.struct.add_uint_field('dc_input_power', 144)
        self.struct.add_uint_field('ac_input_power', 146)

        # Status flags
        self.struct.add_bool_field('ac_output_on', 1509)
        self.struct.add_bool_field('dc_output_on', 2012)
        self.struct.add_bool_field('power_lifting_on', 2021)

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        # Automatically generate polling ranges based on fields defined above
        return self.struct.get_read_holding_registers()

    @property
    def writable_ranges(self) -> List[range]:
        # Define if/where you want to support writing later (e.g. to toggle AC/DC outputs)
        return super().writable_ranges
