from typing import Any, Dict, Self

CONF_TYPE = "type"
CONF_USE_ENCRYPTION = "use_encryption"


class ManufacturerData:
    def __init__(
        self,
        dev_type: str,
        use_encryption: bool,
    ):
        self.dev_type = dev_type
        self.use_encryption = use_encryption

    @staticmethod
    def from_dict(raw: Dict):
        return ManufacturerData(
            raw.get(CONF_TYPE, "Unknown"),
            raw.get(CONF_USE_ENCRYPTION, False),
        )

    @property
    def as_dict(self) -> Dict[str, Any]:
        return {
            CONF_TYPE: self.dev_type,
            CONF_USE_ENCRYPTION: self.use_encryption,
        }
