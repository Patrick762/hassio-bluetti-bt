"""EP760 fields."""
# Taken from EP600, modified to:
# A. Hide Phases 2 and 3 as EP760 in AU is only single phase
# B. Updated DC Solar to incorporate 3rd Input - Note: Relies on additional change to field_attributes.py
from typing import List

from ..utils.commands import ReadHoldingRegisters
from ..base_devices.ProtocolV2Device import ProtocolV2Device


class EP760(ProtocolV2Device):
    def __init__(self, address: str, sn: str):
        super().__init__(address, "EP760", sn)
 # Details
        self.struct.add_uint_field("battery_range_start", 2022)
        self.struct.add_uint_field("battery_range_end", 2023)
        self.struct.add_uint_field("max_ac_input_power", 2213)
        self.struct.add_uint_field("max_ac_input_current", 2214)
        self.struct.add_uint_field("max_ac_output_power", 2215)
        self.struct.add_uint_field("max_ac_output_current", 2216)

        # DC Solar
        self.struct.add_uint_field("pv_input_power1", 1212)
        self.struct.add_decimal_field("pv_input_voltage1", 1213, 1)
        self.struct.add_decimal_field("pv_input_current1", 1214, 1)
        self.struct.add_uint_field("pv_input_power2", 1220)
        self.struct.add_decimal_field("pv_input_voltage2", 1221, 1)
        self.struct.add_decimal_field("pv_input_current2", 1222, 1)
        self.struct.add_uint_field("pv_input_power3", 1228)
        self.struct.add_decimal_field("pv_input_voltage3", 1229, 1)
        self.struct.add_decimal_field("pv_input_current3", 1230, 1)

        # ADL400 Smart Meter for AC Solar
	# Untested 3 Phase
    # EP760 only has 1 phase in Australia
        self.struct.add_uint_field("adl400_ac_input_power_phase1", 1228)
        # self.struct.add_uint_field("adl400_ac_input_power_phase2", 1236)
        # self.struct.add_uint_field("adl400_ac_input_power_phase3", 1244)
        self.struct.add_decimal_field("adl400_ac_input_voltage_phase1", 1229, 1)
        # self.struct.add_decimal_field("adl400_ac_input_voltage_phase2", 1237, 1)
        # self.struct.add_decimal_field("adl400_ac_input_voltage_phase3", 1245, 1)
        # Testing required
        self.struct.add_uint_field("adl400_ac_input_current_phase1", 1230)
        # self.struct.add_uint_field("adl400_ac_input_current_phase2", 1238)
        # self.struct.add_uint_field("adl400_ac_input_current_phase3", 1246)

        # Grid Input
        self.struct.add_decimal_field("grid_frequency", 1300, 1)
        self.struct.add_uint_field("grid_power_phase1", 1313)
        # self.struct.add_uint_field("grid_power_phase2", 1319)
        # self.struct.add_uint_field("grid_power_phase3", 1325)
        self.struct.add_decimal_field("grid_voltage_phase1", 1314, 1)
        # self.struct.add_decimal_field("grid_voltage_phase2", 1320, 1)
        # self.struct.add_decimal_field("grid_voltage_phase3", 1326, 1)
        self.struct.add_decimal_field("grid_current_phase1", 1315, 1)
        # self.struct.add_decimal_field("grid_current_phase2", 1321, 1)
        # self.struct.add_decimal_field("grid_current_phase3", 1327, 1)

        # EP760 AC Output
        self.struct.add_decimal_field("ac_output_frequency", 1500, 1)
        self.struct.add_int_field("ac_output_power_phase1", 1510)
        # self.struct.add_int_field("ac_output_power_phase2", 1517)
        # self.struct.add_int_field("ac_output_power_phase3", 1524)
        self.struct.add_decimal_field("ac_output_voltage_phase1", 1511, 1)
        # self.struct.add_decimal_field("ac_output_voltage_phase2", 1518, 1)
        # self.struct.add_decimal_field("ac_output_voltage_phase3", 1525, 1)
        self.struct.add_decimal_field("ac_output_current_phase1", 1512, 1)
        # self.struct.add_decimal_field("ac_output_current_phase2", 1519, 1)
        # self.struct.add_decimal_field("ac_output_current_phase3", 1526, 1)

        # KM - Consumption
        self.struct.add_int_field("consumption_power_phase1", 1430)
        # self.struct.add_int_field("consumption_power_phase2", 1436)
        # self.struct.add_int_field("consumption_power_phase3", 1442)
        self.struct.add_decimal_field("consumption_voltage_phase1", 1431, 1)
        # self.struct.add_decimal_field("consumption_voltage_phase2", 1437, 1)
        # self.struct.add_decimal_field("consumption_voltage_phase3", 1443, 1)
        self.struct.add_decimal_field("consumption_current_phase1", 1432, 1)
        # self.struct.add_decimal_field("consumption_current_phase2", 1438, 1)
        # self.struct.add_decimal_field("consumption_current_phase3", 1444, 1)

        # KM - Totals
        self.struct.add_uint_field('pv_input_power_all', 144)  # Total PV in
        self.struct.add_uint_field('consumption_power_all', 142)  # Total AC out
        self.struct.add_uint_field('grid_power_all', 146)  # Total Grid in - value only +/- unknown

        # Statistics
        self.struct.add_decimal_field(
            "total_ac_consumption", 152, 1
        )  # Load consumption
        self.struct.add_decimal_field(
            "total_grid_consumption", 156, 1
        )  # Grid consumption stats
        self.struct.add_decimal_field("total_grid_feed", 158, 1)

        # Battery packs
        self.struct.add_swap_string_field("battery_type", 6101, 6)  # internal
        self.struct.add_sn_field("battery_serial_number", 6107)  # internal
        self.struct.add_version_field("bcu_version", 6175)  # internal
        self.struct.add_version_field("bmu_version", 6178)  # internal
        self.struct.add_version_field("safety_module_version", 6181)  # internal
        self.struct.add_version_field("high_voltage_module_version", 6184)  # internal

    @property
    def writable_ranges(self) -> List[range]:
        return super().writable_ranges + [
            range(2022, 2023),
            range(2213,2216),
        ]


    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        return self.struct.get_read_holding_registers()
