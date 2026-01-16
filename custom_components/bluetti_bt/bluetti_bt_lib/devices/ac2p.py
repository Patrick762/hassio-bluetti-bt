"""AC2P fields."""

from typing import List

from ..base_devices.ProtocolV2Device import ProtocolV2Device
from ..utils.commands import ReadHoldingRegisters


class AC2P(ProtocolV2Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "AC2P", sn)

        # Core fields - Using base registers from ProtocolV2Device
        # Note: Don't re-add fields already defined in parent class
        # total_battery_percent (102), device_type (110-115), serial_number (116-119)
        # power_generation (154) are already defined in ProtocolV2Device
        
        # Power stats - These registers may vary by firmware version
        # Trying alternative register addresses based on AC2A and similar devices
        self.struct.add_uint_field('dc_output_power', 140)
        self.struct.add_uint_field('ac_output_power', 142)
        self.struct.add_uint_field('dc_input_power', 144)
        self.struct.add_uint_field('ac_input_power', 146)

        # Status flags - These registers are specific to AC2P
        # If these don't work, try registers from AC70/AC180 (2022, 2023)
        self.struct.add_bool_field('ac_output_on', 1509)
        self.struct.add_bool_field('dc_output_on', 2012)
        self.struct.add_bool_field('power_lifting_on', 2021)

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        # Use explicit polling commands for better reliability
        # This ensures we poll the correct ranges even if struct optimization fails
        return [
            ReadHoldingRegisters(102, 1),    # total_battery_percent
            ReadHoldingRegisters(110, 6),    # device_type
            ReadHoldingRegisters(116, 4),    # serial_number
            ReadHoldingRegisters(140, 8),    # power stats (dc_out, ac_out, dc_in, ac_in)
            ReadHoldingRegisters(154, 1),    # power_generation
            ReadHoldingRegisters(1509, 1),   # ac_output_on
            ReadHoldingRegisters(2012, 1),   # dc_output_on
            ReadHoldingRegisters(2021, 1),   # power_lifting_on
        ]

    @property
    def writable_ranges(self) -> List[range]:
        # Define if/where you want to support writing later (e.g. to toggle AC/DC outputs)
        return super().writable_ranges
