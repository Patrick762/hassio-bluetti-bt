"""EP600 Field definitions.

Changes made here are only temporary and should also be
contributed to https://github.com/warhammerkid/bluetti_mqtt
"""

from typing import List

from bluetti_mqtt.core.devices.bluetti_device import BluettiDevice
from bluetti_mqtt.core.devices.struct import DeviceStruct
from bluetti_mqtt.core.commands import ReadHoldingRegisters

class EP600(BluettiDevice):
    def __init__(self, address: str, sn: str):
        self.struct = DeviceStruct()

        self.struct.add_uint_field('total_battery_percent', 102)
        self.struct.add_swap_string_field('device_type', 110, 6)
        self.struct.add_sn_field('serial_number', 116)
        self.struct.add_decimal_field('power_generation', 154, 1)  # Total power generated since last reset (kwh)
        self.struct.add_swap_string_field('device_type', 1101, 6)
        self.struct.add_sn_field('serial_number', 1107)
        self.struct.add_decimal_field('power_generation', 1202, 1)  # Total power generated since last reset (kwh)
        self.struct.add_uint_field('battery_range_start', 2022)
        self.struct.add_uint_field('battery_range_end', 2023)
        self.struct.add_uint_field('max_ac_input_power', 2213)
        self.struct.add_uint_field('max_ac_input_current', 2214)
        self.struct.add_uint_field('max_ac_output_power', 2215)
        self.struct.add_uint_field('max_ac_output_current', 2216)
        self.struct.add_swap_string_field('battery_type', 6101, 6)
        self.struct.add_sn_field('battery_serial_number', 6107)
        self.struct.add_version_field('bcu_version', 6175)
        self.struct.add_version_field('bmu_version', 6178)
        self.struct.add_version_field('safety_module_version', 6181)
        self.struct.add_version_field('high_voltage_module_version', 6184)

        # DC Solar Input (copied from PR https://github.com/warhammerkid/bluetti_mqtt/pull/87 by KM011092)
        self.struct.add_uint_field('pv_input_power1', 1212)  # MPP 1 in - value * 0.1
        #self.struct.add_uint_field('pv_input_voltage1', 1213)  # MPP 1 in  - value * 0.1
        #self.struct.add_uint_field('pv_input_current1', 1214)  # MPP 1 in
        self.struct.add_uint_field('pv_input_power2', 1220)  # MPP 2 in  - value * 0.1
        #self.struct.add_uint_field('pv_input_voltage2', 1221)  # MPP 2 in  - value * 0.1
        #self.struct.add_uint_field('pv_input_current2', 1222)  # MPP 2 in

        # ADL400 Smart Meter for AC Solar
        self.struct.add_uint_field("adl400_ac_input_power_phase1", 1228)
        self.struct.add_uint_field("adl400_ac_input_power_phase2", 1236)
        self.struct.add_uint_field("adl400_ac_input_power_phase3", 1244)
        self.struct.add_decimal_field("adl400_ac_input_voltage_phase1", 1229, 1)
        self.struct.add_decimal_field("adl400_ac_input_voltage_phase2", 1237, 1)
        self.struct.add_decimal_field("adl400_ac_input_voltage_phase3", 1245, 1)

        # Grid Input
        self.struct.add_decimal_field("grid_input_frequency", 1300, 1)
        self.struct.add_uint_field("grid_input_power_phase1", 1313)
        self.struct.add_uint_field("grid_input_power_phase2", 1319)
        self.struct.add_uint_field("grid_input_power_phase3", 1325)
        self.struct.add_decimal_field("grid_input_voltage_phase1", 1314, 1)
        self.struct.add_decimal_field("grid_input_voltage_phase2", 1320, 1)
        self.struct.add_decimal_field("grid_input_voltage_phase3", 1326, 1)
        self.struct.add_decimal_field("grid_input_current_phase1", 1315, 1)
        self.struct.add_decimal_field("grid_input_current_phase2", 1321, 1)
        self.struct.add_decimal_field("grid_input_current_phase3", 1327, 1)

        # EP600 AC Output
        self.struct.add_decimal_field("ac_output_frequency", 1500, 1)
        self.struct.add_uint_field("ac_output_power_phase1", 1510)
        self.struct.add_uint_field("ac_output_power_phase2", 1517)
        self.struct.add_uint_field("ac_output_power_phase3", 1524)
        self.struct.add_decimal_field("ac_output_voltage_phase1", 1511, 1)
        self.struct.add_decimal_field("ac_output_voltage_phase2", 1518, 1)
        self.struct.add_decimal_field("ac_output_voltage_phase3", 1525, 1)
        self.struct.add_decimal_field("ac_output_current_phase1", 1512, 1)
        self.struct.add_decimal_field("ac_output_current_phase2", 1519, 1)
        self.struct.add_decimal_field("ac_output_current_phase3", 1526, 1)

        super().__init__(address, 'EP600', sn)

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        return [
            ReadHoldingRegisters(100, 62),
            ReadHoldingRegisters(1228, 19),
            ReadHoldingRegisters(1300, 28),
            ReadHoldingRegisters(1500, 27),
            ReadHoldingRegisters(2022, 6),
            ReadHoldingRegisters(2213, 4),
            ReadHoldingRegisters(1212, 11),
            # Battery
            ReadHoldingRegisters(6101, 7),
            ReadHoldingRegisters(6175, 11),
        ]
    
    @property
    def pack_polling_commands(self) -> List[ReadHoldingRegisters]:
        return []

    @property
    def logging_commands(self) -> List[ReadHoldingRegisters]:
        return [
            ReadHoldingRegisters(100, 62),
            ReadHoldingRegisters(1100, 51),
            ReadHoldingRegisters(1200, 90),
            ReadHoldingRegisters(1300, 31),
            ReadHoldingRegisters(1400, 48),
            ReadHoldingRegisters(1500, 30),
            ReadHoldingRegisters(2000, 89),
            ReadHoldingRegisters(2200, 41),
            ReadHoldingRegisters(2300, 36),
            ReadHoldingRegisters(6000, 32),
            ReadHoldingRegisters(6100, 100),
            ReadHoldingRegisters(6300, 100),
        ]
