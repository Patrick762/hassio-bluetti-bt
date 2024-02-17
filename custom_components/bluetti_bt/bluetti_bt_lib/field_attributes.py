"""Field attributes for device fields."""

from dataclasses import dataclass
from enum import Enum, auto, unique

from .field_enums import AutoSleepMode, OutputMode


@unique
class FieldType(Enum):
    NUMERIC = auto()
    BOOL = auto()
    ENUM = auto()
    BUTTON = auto()


@dataclass(frozen=True)
class FieldAttributes:
    type: FieldType
    setter: bool = False
    name: str
    unit_of_measurement: str|None = None
    device_class: str|None = None
    state_class: str|None = None
    options: Enum

@dataclass(frozen=True)
class PowerFieldAttributes(FieldAttributes):
    type = FieldType.NUMERIC
    unit_of_measurement = 'W'
    device_class = 'power'
    state_class = 'measurement'

@dataclass
class VoltageFieldAttributes(FieldAttributes):
    type = FieldType.NUMERIC
    unit_of_measurement = 'V'
    device_class = 'voltage'
    state_class = 'measurement'

@dataclass
class CurrentFieldAttributes(FieldAttributes):
    type = FieldType.NUMERIC
    unit_of_measurement = 'A'
    device_class = 'current'
    state_class = 'measurement'

@dataclass(frozen=True)
class OutletFieldAttributes(FieldAttributes):
    type = FieldType.BOOL
    device_class = 'outlet'

FIELD_ATTRIBUTES = {
    # Base device fields
    'dc_input_power': PowerFieldAttributes(
        name = 'DC Input Power',
    ),
    'ac_input_power': PowerFieldAttributes(
        name = 'AC Input Power',
    ),
    'ac_output_power': PowerFieldAttributes(
        name = 'AC Output Power',
    ),
    'dc_output_power': PowerFieldAttributes(
        name = 'DC Output Power',
    ),
    'power_generation': FieldAttributes(
        type = FieldType.NUMERIC,
        name = 'Total Power Generation',
        unit_of_measurement = 'kWh',
        device_class = 'energy',
        state_class = 'total_increasing',
    ),
    'total_battery_percent': FieldAttributes(
        type = FieldType.NUMERIC,
        name = 'Total Battery Percent',
        unit_of_measurement = '%',
        device_class = 'battery',
        state_class ='measurement',
    ),
    'total_battery_voltage': VoltageFieldAttributes(
        name = 'Total Battery Voltage',
    ),
    'ac_output_on': OutletFieldAttributes(
        name = 'AC Output',
    ),
    'dc_output_on': OutletFieldAttributes(
        name = 'DC Output',
    ),
    'ac_output_on_switch': OutletFieldAttributes(
        name = 'AC Output',
        setter = True,
    ),
    'dc_output_on_switch': OutletFieldAttributes(
        name = 'DC Output',
        setter = True,
    ),

    # Device specific fields
    'ac_output_mode': FieldAttributes(
        type = FieldType.ENUM,
        name = 'AC Output Mode',
        options = OutputMode,
    ),
    'internal_ac_voltage': VoltageFieldAttributes(
        name = 'Internal AC Voltage',
    ),
    'internal_current_one': CurrentFieldAttributes(
        name = 'Internal Current Sensor 1',
    ),
    'internal_power_one': PowerFieldAttributes(
        name = 'Internal Power Sensor 1',
    ),
    'internal_ac_frequency': FieldAttributes(
        type = FieldType.NUMERIC,
        name = 'Internal AC Frequency',
        unit_of_measurement = 'Hz',
        device_class = 'frequency',
        state_class ='measurement',
    ),
    'internal_dc_input_voltage': VoltageFieldAttributes(
        name = 'Internal DC Input Voltage',
    ),
    'internal_dc_input_power': PowerFieldAttributes(
        name = 'Internal DC Input Power',
    ),
    'internal_dc_input_current': CurrentFieldAttributes(
        name = 'Internal DC Input Current',
    ),
    'power_off': FieldAttributes(
        type = FieldType.BUTTON,
        setter = True,
        name = 'Power Off',
    ),
    'auto_sleep_mode': FieldAttributes(
        type = FieldType.ENUM,
        setter = True,
        name = 'Screen Auto Sleep Mode',
        options = AutoSleepMode,
    ),
}

def PACK_FIELD_ATTRIBUTES(pack: int):
    return {
        'pack_voltage': VoltageFieldAttributes(
            name = f'Battery Pack {pack} Voltage',
        ),
        'pack_battery_percent': FieldAttributes(
            type = FieldType,
            name = f'Battery Pack {pack} Percent',
            unit_of_measurement = '%',
            device_class ='battery',
            state_class ='measurement',
        ),
    }
