"""Constants for the Bluetti BT integration."""

from bluetti_mqtt.mqtt_client import MqttFieldConfig, MqttFieldType

DOMAIN = "bluetti_bt"
MANUFACTURER = "Bluetti"

CONF_OPTIONS = "options"

DIAGNOSTIC_FIELDS = [
    "max_ac_input_power",
    "max_ac_input_current",
    "max_ac_output_power",
    "max_ac_output_current",
    "bcu_version",
    "safety_module_version",
    "high_voltage_module_version",
]

ADDITIONAL_DEVICE_FIELDS = {
    "max_ac_input_power": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Max AC Input Power per Phase",
        },
    ),
    "max_ac_input_current": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Max AC Input Current per Phase",
        },
    ),
    "max_ac_output_power": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Max AC Output Power per Phase",
        },
    ),
    "max_ac_output_current": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Max AC Output Current per Phase",
        },
    ),
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
    "high_voltage_module_version": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={"name": "High Voltage Safety Module Version"},
    ),
}
