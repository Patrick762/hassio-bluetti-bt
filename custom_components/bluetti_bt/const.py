"""Constants for the Bluetti BT integration."""

DOMAIN = "bluetti_bt"
MANUFACTURER = "Bluetti"

CONF_OPTIONS = "options"
CONF_USE_CONTROLS = "use_controls"
CONF_PERSISTENT_CONN = "persistent_conn"
CONF_POLLING_INTERVAL = "polling_interval"
CONF_POLLING_TIMEOUT = "polling_timeout"
CONF_MAX_RETRIES = "max_retries"
CONF_ENCRYPTION = "use_encryption"

DATA_COORDINATOR = "coordinator"
DATA_POLLING_RUNNING = "polling_running"

SUPPORTED_MODELS = [
    "AC2A",
    "AC2P",
    "AC60",
    "AC70",
    "AC180",
    "AC180P",
    "AC200L",
    "AC200M",
    "AC300",
    "AC500",
    "EB3A",
    "EP500",
    "EP500P",
    "EP600",
    "EP760",
    "EP800",
]

CONTROL_FIELDS = [
    "ac_output_on_switch",
    "dc_output_on_switch",
    "power_off",
    "eco_on",
    "power_lifting_on",
    "grid_enhancement_mode_on",
    "silent_charging_on",
]

DIAGNOSTIC_FIELDS = [
    "max_ac_input_power",
    "max_ac_input_current",
    "max_ac_output_power",
    "max_ac_output_current",
    "bcu_version",
    "dsp_version",
    "arm_version",
    "safety_module_version",
    "high_voltage_module_version",
    "power_generation",
    "total_ac_consumption",
    "total_grid_consumption",
    "total_grid_feed",
    "ac_input_voltage",
]
