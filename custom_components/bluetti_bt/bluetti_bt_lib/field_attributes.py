"""Field attributes for device fields."""

from dataclasses import dataclass
from enum import Enum, auto, unique


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
        device_class ='battery',
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
