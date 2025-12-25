from homeassistant.const import EntityCategory
from bluetti_bt_lib import FieldName


DIAGNOSTICS = [
    FieldName.VER_ARM,
    FieldName.VER_DSP,
]

CONFIGS = [
    FieldName.CTRL_ECO,
    FieldName.CTRL_ECO_TIME_MODE,
    FieldName.CTRL_CHARGING_MODE,
    FieldName.CTRL_POWER_LIFTING,
]


def get_category(field: FieldName) -> EntityCategory | None:
    if field in DIAGNOSTICS:
        return EntityCategory.DIAGNOSTIC
    if field in CONFIGS:
        return EntityCategory.CONFIG
    return None
