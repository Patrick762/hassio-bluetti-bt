"""Field attributes for device fields."""

from enum import Enum, auto, unique

from .field_enums import (
    AutoSleepMode,
    ChargingMode,
    EcoShutdown,
    LedMode,
    OutputMode,
    SplitPhaseMachineType,
    UpsMode,
)


@unique
class FieldType(Enum):
    NUMERIC = auto()
    BOOL = auto()
    ENUM = auto()


class FieldAttributes:
    def __init__(
        self,
        type: FieldType = FieldType.NUMERIC,
        setter: bool = False,
        name: str = "",
        unit_of_measurement: str | None = None,
        device_class: str | None = None,
        state_class: str | None = None,
        options: Enum | None = None,
    ):
        self.type = type
        self.setter = setter
        self.name = name
        self.unit_of_measurement = unit_of_measurement
        self.device_class = device_class
        self.state_class = state_class
        self.options = options


class PowerFieldAttributes(FieldAttributes):
    def __init__(
        self,
        name: str = "",
    ):
        super().__init__(
            name=name,
            unit_of_measurement="W",
            device_class="power",
            state_class="measurement",
        )


class VoltageFieldAttributes(FieldAttributes):
    def __init__(
        self,
        name: str = "",
    ):
        super().__init__(
            name=name,
            unit_of_measurement="V",
            device_class="voltage",
            state_class="measurement",
        )


class CurrentFieldAttributes(FieldAttributes):
    def __init__(
        self,
        name: str = "",
    ):
        super().__init__(
            name=name,
            unit_of_measurement="A",
            device_class="current",
            state_class="measurement",
        )


class EnergyFieldAttributes(FieldAttributes):
    def __init__(
        self,
        name: str = "",
    ):
        super().__init__(
            name=name,
            unit_of_measurement="kWh",
            device_class="energy",
            state_class="total_increasing",
        )


class FrequencyFieldAttributes(FieldAttributes):
    def __init__(
        self,
        name: str = "",
    ):
        super().__init__(
            name=name,
            unit_of_measurement="Hz",
            device_class="frequency",
            state_class="measurement",
        )


class OutletFieldAttributes(FieldAttributes):
    def __init__(
        self,
        name: str = "",
        setter: bool = False,
    ):
        super().__init__(
            type=FieldType.BOOL,
            name=name,
            setter=setter,
            device_class="outlet",
        )


FIELD_ATTRIBUTES: dict[str, FieldAttributes] = {
    # Base device fields
    "dc_input_power": PowerFieldAttributes("DC Input Power"),
    "ac_input_power": PowerFieldAttributes("AC Input Power"),
    "ac_output_power": PowerFieldAttributes("AC Output Power"),
    "dc_output_power": PowerFieldAttributes("DC Output Power"),
    "dsp_version": FieldAttributes(
        type=FieldType.NUMERIC,
        name=f"DSP Version",
    ),
    "arm_version": FieldAttributes(
        type=FieldType.NUMERIC,
        name=f"ARM Version",
    ),
    "power_generation": EnergyFieldAttributes("Total Power Generation"),
    "total_battery_percent": FieldAttributes(
        type=FieldType.NUMERIC,
        name="Total Battery Percent",
        unit_of_measurement="%",
        device_class="battery",
        state_class="measurement",
    ),
    "total_battery_voltage": VoltageFieldAttributes("Total Battery Voltage"),
    "ac_output_on": OutletFieldAttributes("AC Output"),
    "dc_output_on": OutletFieldAttributes("DC Output"),
    # Controls
    "ac_output_on_switch": OutletFieldAttributes(
        name="AC Output",
        setter=True,
    ),
    "dc_output_on_switch": OutletFieldAttributes(
        name="DC Output",
        setter=True,
    ),
    # Device specific fields
    "ac_output_mode": FieldAttributes(
        type=FieldType.ENUM,
        name="AC Output Mode",
        options=OutputMode,
    ),
    "internal_ac_voltage": VoltageFieldAttributes("Internal AC Voltage"),
    "internal_current_one": CurrentFieldAttributes("Internal Current Sensor 1"),
    "internal_power_one": PowerFieldAttributes("Internal Power Sensor 1"),
    "internal_ac_frequency": FrequencyFieldAttributes("Internal AC Frequency"),
    "internal_current_two": CurrentFieldAttributes("Internal Current Sensor 2"),
    "internal_power_two": PowerFieldAttributes("Internal Power Sensor 2"),
    "ac_input_voltage": VoltageFieldAttributes("AC Input Voltage"),
    "internal_current_three": CurrentFieldAttributes("Internal Current Sensor 3"),
    "internal_power_three": PowerFieldAttributes("Internal Power Sensor 3"),
    "ac_input_frequency": FrequencyFieldAttributes("AC Input Frequency"),
    "internal_dc_input_voltage": VoltageFieldAttributes("Internal DC Input Voltage"),
    "internal_dc_input_power": PowerFieldAttributes("Internal DC Input Power"),
    "internal_dc_input_current": CurrentFieldAttributes("Internal DC Input Current"),
    "pv_input_power1": PowerFieldAttributes("Solar Input Power 1"),
    "pv_input_power2": PowerFieldAttributes("Solar Input Power 2"),
    "pv_input_voltage1": VoltageFieldAttributes("Solar Input Voltage 1"),
    "pv_input_voltage2": VoltageFieldAttributes("Solar Input Voltage 2"),
    "pv_input_current1": CurrentFieldAttributes("Solar Input Current 1"),
    "pv_input_current2": CurrentFieldAttributes("Solar Input Current 2"),
    "adl400_ac_input_power_phase1": PowerFieldAttributes(
        "AC Solar Input Power Phase 1"
    ),
    "adl400_ac_input_power_phase2": PowerFieldAttributes(
        "AC Solar Input Power Phase 2"
    ),
    "adl400_ac_input_power_phase3": PowerFieldAttributes(
        "AC Solar Input Power Phase 3"
    ),
    "adl400_ac_input_voltage_phase1": VoltageFieldAttributes(
        "AC Solar Input Voltage Phase 1"
    ),
    "adl400_ac_input_voltage_phase2": VoltageFieldAttributes(
        "AC Solar Input Voltage Phase 2"
    ),
    "adl400_ac_input_voltage_phase3": VoltageFieldAttributes(
        "AC Solar Input Voltage Phase 3"
    ),
    "adl400_ac_input_current_phase1": CurrentFieldAttributes(
        "AC Solar Input Current Phase 1"
    ),
    "adl400_ac_input_current_phase2": CurrentFieldAttributes(
        "AC Solar Input Current Phase 2"
    ),
    "adl400_ac_input_current_phase3": CurrentFieldAttributes(
        "AC Solar Input Current Phase 3"
    ),
    "grid_frequency": FrequencyFieldAttributes("Grid Frequency"),
    "grid_power_phase1": PowerFieldAttributes("Grid Power Phase 1"),
    "grid_power_phase2": PowerFieldAttributes("Grid Power Phase 2"),
    "grid_power_phase3": PowerFieldAttributes("Grid Power Phase 3"),
    "grid_voltage_phase1": VoltageFieldAttributes("Grid Voltage Phase 1"),
    "grid_voltage_phase2": VoltageFieldAttributes("Grid Voltage Phase 2"),
    "grid_voltage_phase3": VoltageFieldAttributes("Grid Voltage Phase 3"),
    "grid_current_phase1": CurrentFieldAttributes("Grid Current Phase 1"),
    "grid_current_phase2": CurrentFieldAttributes("Grid Current Phase 2"),
    "grid_current_phase3": CurrentFieldAttributes("Grid Current Phase 3"),
    "ac_output_frequency": FrequencyFieldAttributes("AC Output Frequency"),
    "ac_output_power_phase1": PowerFieldAttributes("AC Output Power Phase 1"),
    "ac_output_power_phase2": PowerFieldAttributes("AC Output Power Phase 2"),
    "ac_output_power_phase3": PowerFieldAttributes("AC Output Power Phase 3"),
    "ac_output_voltage_phase1": VoltageFieldAttributes("AC Output Voltage Phase 1"),
    "ac_output_voltage_phase2": VoltageFieldAttributes("AC Output Voltage Phase 2"),
    "ac_output_voltage_phase3": VoltageFieldAttributes("AC Output Voltage Phase 3"),
    "total_ac_consumption": EnergyFieldAttributes("Total Load Consumption"),
    "total_grid_consumption": EnergyFieldAttributes("Total Grid Consumption"),
    "total_grid_feed": EnergyFieldAttributes("Total Grid Feed"),

    # KM - Consumption
    "consumption_power_phase1": PowerFieldAttributes("Consumption Power Phase 1"),
    "consumption_power_phase2": PowerFieldAttributes("Consumption Power Phase 2"),
    "consumption_power_phase3": PowerFieldAttributes("Consumption Power Phase 3"),
    "consumption_voltage_phase1": VoltageFieldAttributes("Consumption Voltage Phase 1"),
    "consumption_voltage_phase2": VoltageFieldAttributes("Consumption Voltage Phase 2"),
    "consumption_voltage_phase3": VoltageFieldAttributes("Consumption Voltage Phase 3"),
    "consumption_current_phase1": CurrentFieldAttributes("Consumption Current Phase 1"),
    "consumption_current_phase2": CurrentFieldAttributes("Consumption Current Phase 2"),
    "consumption_current_phase3": CurrentFieldAttributes("Consumption Current Phase 3"),
    # KM - Consumption end

    # KM - Totals
    "pv_input_power_all": PowerFieldAttributes("PV Input Power All"),
    "consumption_power_all": PowerFieldAttributes("Consumption Power All"),
    "grid_power_all": PowerFieldAttributes("Grid Power All"),
    # KM - Totals end


    # Device specific controls
    "power_off": FieldAttributes(
        type=FieldType.BOOL,
        setter=True,
        name="Power Off",
    ),
    "auto_sleep_mode": FieldAttributes(
        type=FieldType.ENUM,
        setter=True,
        name="Screen Auto Sleep Mode",
        options=AutoSleepMode,
    ),
    "ups_mode": FieldAttributes(
        type=FieldType.ENUM,
        setter=False,  # Disabled for safety reasons
        name="UPS Working Mode",
        options=UpsMode,
    ),
    "split_phase_on": FieldAttributes(
        type=FieldType.BOOL,
        setter=False,  # Disabled for safety reasons
        name="Split Phase",
    ),
    "split_phase_machine_mode": FieldAttributes(
        type=FieldType.ENUM,
        setter=False,  # Disabled for safety reasons
        name="Split Phase Machine Type",
        options=SplitPhaseMachineType,
    ),
    "grid_charge_on": FieldAttributes(
        type=FieldType.BOOL,
        setter=False,  # Disabled for safety reasons
        name="Grid Charge",
    ),
    "time_control_on": FieldAttributes(
        type=FieldType.BOOL,
        setter=False,  # Disabled for safety reasons
        name="Time Control",
    ),
    "battery_range_start": FieldAttributes(
        type=FieldType.NUMERIC,
        setter=False,  # Disabled
        name="Battery Range Start",
        unit_of_measurement="%",
    ),
    "battery_range_end": FieldAttributes(
        type=FieldType.NUMERIC,
        setter=False,  # Disabled
        name="Battery Range End",
        unit_of_measurement="%",
    ),
    "led_mode": FieldAttributes(
        type=FieldType.ENUM,
        setter=True,
        name="LED Mode",
        options=LedMode,
    ),
    "eco_on": FieldAttributes(
        type=FieldType.BOOL,
        setter=True,
        name="Eco Mode",
    ),
    "eco_shutdown": FieldAttributes(
        type=FieldType.ENUM,
        setter=True,
        name="Eco Shutdown",
        options=EcoShutdown,
    ),
    "charging_mode": FieldAttributes(
        type=FieldType.ENUM,
        setter=True,
        name="Charging Mode",
        options=ChargingMode,
    ),
    "power_lifting_on": FieldAttributes(
        type=FieldType.BOOL,
        setter=True,
        name="Power Lifting",
    ),
    "grid_enhancement_mode_on": FieldAttributes(
        type=FieldType.BOOL,
        setter=True,
        name="Grid Enhancement Mode",
    ),
    "silent_charging_on": FieldAttributes(
        type=FieldType.BOOL,
        setter=True,
        name="Silent Charging",
    ),
}


def PACK_FIELD_ATTRIBUTES(pack: int):
    return {
        "pack_voltage": VoltageFieldAttributes(
            name=f"Battery Pack {pack} Voltage",
        ),
        "pack_battery_percent": FieldAttributes(
            type=FieldType.NUMERIC,
            name=f"Battery Pack {pack} Percent",
            unit_of_measurement="%",
            device_class="battery",
            state_class="measurement",
        ),
        "pack_bms_version": FieldAttributes(
            type=FieldType.NUMERIC,
            name=f"Battery Pack {pack} BMS Version",
        ),
    }
