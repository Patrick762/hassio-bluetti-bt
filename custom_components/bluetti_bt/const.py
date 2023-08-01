"""Constants for the Bluetti BT integration."""

from bluetti_mqtt.mqtt_client import MqttFieldConfig, MqttFieldType

DOMAIN = "bluetti_bt"
MANUFACTURER = "Bluetti"

CONF_OPTIONS = "options"

DIAGNOSTIC_FIELDS = [
    "bcu_version",
    "safety_module_version",
]

ADDITIONAL_DEVICE_FIELDS = {
    "bcu_version": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={"name": "BCU Version"},
    ),
    "safety_module_version": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={"name": "Safety Module Version"},
    ),
}
