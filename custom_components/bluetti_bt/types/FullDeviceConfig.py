from typing import Any, Dict

from .InitialDeviceConfig import InitialDeviceConfig
from .OptionalDeviceConfig import OptionalDeviceConfig


class FullDeviceConfig:
    def __init__(
        self,
        initial: InitialDeviceConfig,
        optional: OptionalDeviceConfig,
    ):
        self.address = initial.address
        self.name = initial.name
        self.dev_type = initial.dev_type
        self.use_encryption = initial.use_encryption
        self.use_controls = optional.use_controls
        self.persistent_conn = optional.persistent_conn
        self.polling_interval = optional.polling_interval
        self.polling_timeout = optional.polling_timeout
        self.max_retries = optional.max_retries

    @staticmethod
    def from_dict(raw: Dict[str, Any]):
        initial = InitialDeviceConfig.from_dict(raw)

        if initial is None:
            return None

        return FullDeviceConfig(
            initial,
            OptionalDeviceConfig.from_dict(raw),
        )
