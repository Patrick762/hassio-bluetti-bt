"""Constants for the Bluetti BT integration."""

DOMAIN = "bluetti_bt"
MANUFACTURER = "Bluetti"

CONF_OPTIONS = "options"
CONF_USE_CONTROLS = "use_controls"
CONF_PERSISTENT_CONN = "persistent_conn"
CONF_POLLING_INTERVAL = "polling_interval"
CONF_POLLING_TIMEOUT = "polling_timeout"
CONF_MAX_RETRIES = "max_retries"

DATA_COORDINATOR = "coordinator"
DATA_POLLING_RUNNING = "polling_running"

SUPPORTED_MODELS = [
    "AC60",
    "AC200M",
    "AC300",
    "AC500",
    "EB3A",
    "EP500",
    "EP500P",
    "EP600",
    "EP760",
]

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
