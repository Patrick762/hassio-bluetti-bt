from typing import Dict
from homeassistant.components.sensor import SensorDeviceClass
from bluetti_bt_lib import FieldName


FIELD_DEVICE_CLASS: Dict[FieldName, SensorDeviceClass] = {
    FieldName.AC_INPUT_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.AC_INPUT_FREQUENCY: SensorDeviceClass.FREQUENCY,
    FieldName.AC_INPUT_POWER: SensorDeviceClass.POWER,
    FieldName.AC_INPUT_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.AC_OUTPUT_FREQUENCY: SensorDeviceClass.FREQUENCY,
    FieldName.AC_OUTPUT_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.AC_OUTPUT_POWER: SensorDeviceClass.POWER,
    FieldName.AC_OUTPUT_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.AC_P1_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.AC_P1_POWER: SensorDeviceClass.POWER,
    FieldName.AC_P1_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.AC_P2_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.AC_P2_POWER: SensorDeviceClass.POWER,
    FieldName.AC_P2_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.AC_P3_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.AC_P3_POWER: SensorDeviceClass.POWER,
    FieldName.AC_P3_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.BATTERY_SOC: SensorDeviceClass.BATTERY,
    FieldName.DC_INPUT_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.DC_INPUT_POWER: SensorDeviceClass.POWER,
    FieldName.DC_INPUT_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.DC_OUTPUT_POWER: SensorDeviceClass.POWER,
    FieldName.GRID_FREQUENCY: SensorDeviceClass.FREQUENCY,
    FieldName.GRID_P1_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.GRID_P1_POWER: SensorDeviceClass.POWER,
    FieldName.GRID_P1_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.GRID_P2_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.GRID_P2_POWER: SensorDeviceClass.POWER,
    FieldName.GRID_P2_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.GRID_P3_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.GRID_P3_POWER: SensorDeviceClass.POWER,
    FieldName.GRID_P3_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.INTERNAL_AC_FREQUENCY: SensorDeviceClass.FREQUENCY,
    FieldName.INTERNAL_AC_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.INTERNAL_DC_INPUT_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.INTERNAL_DC_INPUT_POWER: SensorDeviceClass.POWER,
    FieldName.INTERNAL_DC_INPUT_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.POWER_GENERATION: SensorDeviceClass.ENERGY,
    FieldName.PV_S1_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.PV_S1_POWER: SensorDeviceClass.POWER,
    FieldName.PV_S1_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.PV_S2_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.PV_S2_POWER: SensorDeviceClass.POWER,
    FieldName.PV_S2_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.SM_P1_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.SM_P1_POWER: SensorDeviceClass.POWER,
    FieldName.SM_P1_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.SM_P2_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.SM_P2_POWER: SensorDeviceClass.POWER,
    FieldName.SM_P2_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.SM_P3_CURRENT: SensorDeviceClass.CURRENT,
    FieldName.SM_P3_POWER: SensorDeviceClass.POWER,
    FieldName.SM_P3_VOLTAGE: SensorDeviceClass.VOLTAGE,
    FieldName.TIME_REMAINING: SensorDeviceClass.DURATION,
    # Battery packs
    FieldName.PACK_BATTERY_SOC: SensorDeviceClass.BATTERY,
    FieldName.PACK_CELL_VOLTAGES: SensorDeviceClass.VOLTAGE,
    FieldName.PACK_VOLTAGE: SensorDeviceClass.VOLTAGE,
}


def get_device_class(field: FieldName) -> str | None:
    device_class = FIELD_DEVICE_CLASS.get(field)

    if device_class is None:
        return None

    return device_class.value
