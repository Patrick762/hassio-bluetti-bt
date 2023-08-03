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
    "adl400_ac_input_voltage_phase1": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "ADL400 AC Input Voltage Phase 1",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "adl400_ac_input_voltage_phase2": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "ADL400 AC Input Voltage Phase 2",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "adl400_ac_input_voltage_phase3": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "ADL400 AC Input Voltage Phase 3",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "ac_input_voltage_phase1": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "AC Input Voltage Phase 1",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "ac_input_voltage_phase2": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "AC Input Voltage Phase 2",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "ac_input_voltage_phase3": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "AC Input Voltage Phase 3",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "ac_output_voltage_phase1": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "AC Output Voltage Phase 1",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "ac_output_voltage_phase2": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "AC Output Voltage Phase 2",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "ac_output_voltage_phase3": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "AC Output Voltage Phase 3",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "ac_output_frequency": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "AC Output Frequency",
            "unit_of_measurement": "Hz",
            "device_class": "frequency",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
}
