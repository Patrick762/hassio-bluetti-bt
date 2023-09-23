"""Constants for the Bluetti BT integration."""

from bluetti_mqtt.mqtt_client import MqttFieldConfig, MqttFieldType

DOMAIN = "bluetti_bt"
MANUFACTURER = "Bluetti"

CONF_OPTIONS = "options"
CONF_USE_CONTROLS = "use_controls"
CONF_PERSISTENT_CONN = "persistent_conn"
CONF_POLLING_INTERVAL = "polling_interval"

DATA_COORDINATOR = "coordinator"
DATA_POLLING_RUNNING = "polling_running"

CONTROL_FIELDS = [
    "ac_output_on",
    "dc_output_on",
]

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
    'pv_input_power1': MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Solar Input Power 1",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    'pv_input_voltage1': MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Solar Input Voltage 1",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    'pv_input_current1': MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Solar Input Current 1",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    'pv_input_power2': MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Solar Input Power 2",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    'pv_input_voltage2': MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Solar Input Voltage 2",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    'pv_input_current2': MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Solar Input Current 2",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "adl400_ac_input_power_phase1": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "ADL400 AC Input Power Phase 1",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "adl400_ac_input_power_phase2": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "ADL400 AC Input Power Phase 2",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "adl400_ac_input_power_phase3": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "ADL400 AC Input Power Phase 3",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
            "force_update": True,
        },
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
    "grid_input_voltage_phase1": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Grid Input Voltage Phase 1",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "grid_input_voltage_phase2": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Grid Input Voltage Phase 2",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "grid_input_voltage_phase3": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Grid Input Voltage Phase 3",
            "unit_of_measurement": "V",
            "device_class": "voltage",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "grid_input_current_phase1": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Grid Input Current Phase 1",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "grid_input_current_phase2": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Grid Input Current Phase 2",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "grid_input_current_phase3": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Grid Input Current Phase 3",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "grid_input_power_phase1": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Grid Input Power Phase 1",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "grid_input_power_phase2": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Grid Input Power Phase 2",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "grid_input_power_phase3": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Grid Input Power Phase 3",
            "unit_of_measurement": "W",
            "device_class": "power",
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
    "ac_output_power_phase1": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "AC Output Power Phase 1",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "ac_output_power_phase2": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "AC Output Power Phase 2",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "ac_output_power_phase3": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "AC Output Power Phase 3",
            "unit_of_measurement": "W",
            "device_class": "power",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "ac_output_current_phase1": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "AC Output Current Phase 1",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "ac_output_current_phase2": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "AC Output Current Phase 2",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "ac_output_current_phase3": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "AC Output Current Phase 3",
            "unit_of_measurement": "A",
            "device_class": "current",
            "state_class": "measurement",
            "force_update": True,
        },
    ),
    "testing0": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Register Testing 0",
        },
    ),
    "testing1": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Register Testing 1",
        },
    ),
    "testing2": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Register Testing 2",
        },
    ),
    "testing3": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Register Testing 3",
        },
    ),
    "testing4": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Register Testing 4",
        },
    ),
    "testing5": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Register Testing 5",
        },
    ),
    "testing6": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Register Testing 6",
        },
    ),
    "testing7": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Register Testing 7",
        },
    ),
    "testing8": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Register Testing 8",
        },
    ),
    "testing9": MqttFieldConfig(
        type=MqttFieldType.NUMERIC,
        setter=False,
        advanced=False,
        home_assistant_extra={
            "name": "Register Testing 9",
        },
    ),
}
