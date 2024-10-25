"""Unittest for device struct."""

import unittest

from custom_components.bluetti_bt.bluetti_bt_lib.utils.commands import ReadHoldingRegisters
from custom_components.bluetti_bt.bluetti_bt_lib.utils.struct import DeviceStruct

class TestDeviceStruct(unittest.TestCase):
    def test_get_read_holding_registers(self):
        struct = DeviceStruct()

        struct.add_swap_string_field("device_type", 110, 6)
        struct.add_sn_field("serial_number", 116)
        struct.add_decimal_field(
            "power_generation", 154, 1
        )
        struct.add_uint_field("total_battery_percent", 102)

        registers = struct.get_read_holding_registers()

        self.assertGreater(len(registers), 0)

        for reg in registers:
            self.assertIsInstance(reg, ReadHoldingRegisters)
