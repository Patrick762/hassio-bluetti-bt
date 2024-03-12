"""EB3A fields."""

from typing import List

from ..utils.commands import ReadHoldingRegisters
from ..field_enums import ChargingMode, EcoShutdown, LedMode
from ..base_devices.ProtocolV1Device import ProtocolV1Device


class EB3A(ProtocolV1Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "EB3A", sn)

        # Details
        self.struct.add_decimal_field("ac_input_voltage", 77, 1)
        self.struct.add_uint_field("internal_dc_input_voltage", 86)

        # Controls
        self.struct.add_enum_field("led_mode", 3034, LedMode)
        self.struct.add_bool_field("power_off", 3060)
        self.struct.add_bool_field("eco_on", 3063)
        self.struct.add_enum_field("eco_shutdown", 3064, EcoShutdown)
        self.struct.add_enum_field("charging_mode", 3065, ChargingMode)
        self.struct.add_bool_field("power_lifting_on", 3066)

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        return super().polling_commands + [
            ReadHoldingRegisters(77, 1),
            ReadHoldingRegisters(86, 1),
            ReadHoldingRegisters(3034, 1),
            ReadHoldingRegisters(3060, 1),
            ReadHoldingRegisters(3063, 5),
        ]

    @property
    def writable_ranges(self) -> List[range]:
        return super().writable_ranges + [
            range(3034, 3035),
            range(3060, 3061),
            range(3063, 3067),
        ]
