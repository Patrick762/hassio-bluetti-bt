from typing import Dict
from homeassistant.components.sensor import SensorStateClass
from bluetti_bt_lib.fields import FieldName


FIELD_STATE_CLASS: Dict[FieldName, SensorStateClass] = {
    FieldName.AC_INPUT_FREQUENCY: SensorStateClass.MEASUREMENT,
    FieldName.AC_INPUT_POWER: SensorStateClass.MEASUREMENT,
    FieldName.AC_INPUT_VOLTAGE: SensorStateClass.MEASUREMENT,
    FieldName.AC_OUTPUT_FREQUENCY: SensorStateClass.MEASUREMENT,
    FieldName.AC_OUTPUT_POWER: SensorStateClass.MEASUREMENT,
    FieldName.AC_P1_CURRENT: SensorStateClass.MEASUREMENT,
    FieldName.AC_P1_POWER: SensorStateClass.MEASUREMENT,
    FieldName.AC_P1_VOLTAGE: SensorStateClass.MEASUREMENT,
    FieldName.AC_P2_CURRENT: SensorStateClass.MEASUREMENT,
    FieldName.AC_P2_POWER: SensorStateClass.MEASUREMENT,
    FieldName.AC_P2_VOLTAGE: SensorStateClass.MEASUREMENT,
    FieldName.AC_P3_CURRENT: SensorStateClass.MEASUREMENT,
    FieldName.AC_P3_POWER: SensorStateClass.MEASUREMENT,
    FieldName.AC_P3_VOLTAGE: SensorStateClass.MEASUREMENT,
    FieldName.BATTERY_SOC: SensorStateClass.MEASUREMENT,
    FieldName.DC_INPUT_POWER: SensorStateClass.MEASUREMENT,
    FieldName.DC_OUTPUT_POWER: SensorStateClass.MEASUREMENT,
    FieldName.GRID_FREQUENCY: SensorStateClass.MEASUREMENT,
    FieldName.GRID_P1_CURRENT: SensorStateClass.MEASUREMENT,
    FieldName.GRID_P1_POWER: SensorStateClass.MEASUREMENT,
    FieldName.GRID_P1_VOLTAGE: SensorStateClass.MEASUREMENT,
    FieldName.GRID_P2_CURRENT: SensorStateClass.MEASUREMENT,
    FieldName.GRID_P2_POWER: SensorStateClass.MEASUREMENT,
    FieldName.GRID_P2_VOLTAGE: SensorStateClass.MEASUREMENT,
    FieldName.GRID_P3_CURRENT: SensorStateClass.MEASUREMENT,
    FieldName.GRID_P3_POWER: SensorStateClass.MEASUREMENT,
    FieldName.GRID_P3_VOLTAGE: SensorStateClass.MEASUREMENT,
    FieldName.INTERNAL_AC_FREQUENCY: SensorStateClass.MEASUREMENT,
    FieldName.INTERNAL_AC_VOLTAGE: SensorStateClass.MEASUREMENT,
    FieldName.INTERNAL_DC_INPUT_CURRENT: SensorStateClass.MEASUREMENT,
    FieldName.INTERNAL_DC_INPUT_POWER: SensorStateClass.MEASUREMENT,
    FieldName.INTERNAL_DC_INPUT_VOLTAGE: SensorStateClass.MEASUREMENT,
    FieldName.POWER_GENERATION: SensorStateClass.TOTAL_INCREASING,
    FieldName.PV_S1_CURRENT: SensorStateClass.MEASUREMENT,
    FieldName.PV_S1_POWER: SensorStateClass.MEASUREMENT,
    FieldName.PV_S1_VOLTAGE: SensorStateClass.MEASUREMENT,
    FieldName.PV_S2_CURRENT: SensorStateClass.MEASUREMENT,
    FieldName.PV_S2_POWER: SensorStateClass.MEASUREMENT,
    FieldName.PV_S2_VOLTAGE: SensorStateClass.MEASUREMENT,
    FieldName.SM_P1_CURRENT: SensorStateClass.MEASUREMENT,
    FieldName.SM_P1_POWER: SensorStateClass.MEASUREMENT,
    FieldName.SM_P1_VOLTAGE: SensorStateClass.MEASUREMENT,
    FieldName.SM_P2_CURRENT: SensorStateClass.MEASUREMENT,
    FieldName.SM_P2_POWER: SensorStateClass.MEASUREMENT,
    FieldName.SM_P2_VOLTAGE: SensorStateClass.MEASUREMENT,
    FieldName.SM_P3_CURRENT: SensorStateClass.MEASUREMENT,
    FieldName.SM_P3_POWER: SensorStateClass.MEASUREMENT,
    FieldName.SM_P3_VOLTAGE: SensorStateClass.MEASUREMENT,
}


def get_state_class(field: FieldName) -> str:
    state_class = FIELD_STATE_CLASS.get(field)

    if state_class is None:
        return None

    return state_class.value
