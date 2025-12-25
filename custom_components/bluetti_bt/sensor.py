"""Bluetti BT sensors."""

from __future__ import annotations
from enum import Enum
import logging
from decimal import Decimal
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from bluetti_bt_lib import build_device, FieldName, get_unit

from . import device_info as dev_info, get_unique_id, FullDeviceConfig
from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import PollingCoordinator
from .utils import unique_id_logable
from .types import get_device_class, get_state_class, get_category

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup sensor entities."""

    config = FullDeviceConfig.from_dict(entry.data)
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    if config is None or not isinstance(coordinator, PollingCoordinator):
        _LOGGER.error("No coordinator found")
        return None

    # Generate device info
    _LOGGER.info("Creating sensors for device with address %s", config.address)
    device_info = dev_info(entry)

    # Add sensors
    bluetti_device = build_device(config.name)

    sensors_to_add = []
    sensor_fields = bluetti_device.get_sensor_fields()

    for field in sensor_fields:
        field_name = FieldName(field.name)

        if field_name in [FieldName.DEVICE_TYPE, FieldName.DEVICE_SN]:
            continue

        unit = get_unit(field_name)
        device_class = get_device_class(field_name)
        state_class = get_state_class(field_name)
        category = get_category(field_name)

        if unit is not None:
            sensors_to_add.append(
                BluettiSensor(
                    coordinator,
                    device_info,
                    field.address,
                    field.name,
                    unit_of_measurement=unit,
                    device_class=device_class,
                    state_class=state_class,
                    category=category,
                )
            )
        else:
            sensors_to_add.append(
                BluettiSensor(
                    coordinator,
                    device_info,
                    field.address,
                    field.name,
                    category=category,
                )
            )

    async_add_entities(sensors_to_add)


class BluettiSensor(CoordinatorEntity, SensorEntity):
    """Bluetti universal sensor."""

    def __init__(
        self,
        coordinator: PollingCoordinator,
        device_info: DeviceInfo,
        address,
        response_key: str,
        unit_of_measurement: str | None = None,
        device_class: str | None = None,
        state_class: str | None = None,
        category: EntityCategory | None = None,
        options: list[str] | None = None,
    ):
        """Init sensor entity."""
        super().__init__(coordinator)
        self.coordinator = coordinator

        self._attr_has_entity_name = True
        e_name = f"{device_info.get('name')} {response_key}"
        self._address = address
        self._response_key = response_key
        self._unavailable_counter = 0

        self._attr_device_info = device_info
        self._attr_translation_key = response_key
        self._attr_available = False
        self._attr_unique_id = get_unique_id(e_name)
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_entity_category = category
        self._options = options

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._attr_available

    def _set_available(self):
        """Set sensor as available."""
        self._attr_available = True
        self._unavailable_counter = 0
        self._attr_extra_state_attributes = {}
        self.async_write_ha_state()

    def _set_unavailable(self, cause: str = "Unknown"):
        """Set sensor as unavailable."""
        self._unavailable_counter += 1

        self._attr_extra_state_attributes = {
            "unavailable_counter": self._unavailable_counter,
            "unavailable_cause": cause,
        }

        if self._unavailable_counter >= 5:
            self._attr_available = False

        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data is None:
            _LOGGER.debug(
                "Data from coordinator is None",
            )
            self._set_unavailable("Data is None")
            return

        _LOGGER.debug("Updating state of %s", unique_id_logable(self._attr_unique_id))
        if not isinstance(self.coordinator.data, dict):
            _LOGGER.warning(
                "Invalid data from coordinator (sensor.%s)",
                unique_id_logable(self._attr_unique_id),
            )
            self._set_unavailable("Invalid data")
            return

        response_data = self.coordinator.data.get(self._response_key)
        if response_data is None:
            _LOGGER.debug("No data for available for (%s)", self._response_key)
            self._set_unavailable("No data")
            return

        if (
            not isinstance(response_data, int)
            and not isinstance(response_data, float)
            and not isinstance(response_data, complex)
            and not isinstance(response_data, Decimal)
            and not isinstance(response_data, Enum)
            and not isinstance(response_data, str)
        ):
            _LOGGER.warning(
                "Invalid response data type from coordinator (sensor.%s): %s has type %s",
                unique_id_logable(self._attr_unique_id),
                response_data,
                type(response_data),
            )
            self._set_unavailable("Invalid data type")
            return

        self._set_available()

        # Different for enum and numeric
        if self._options is not None and isinstance(response_data, Enum):
            # Enum
            self._attr_native_value = response_data.name
        else:
            # Numeric
            self._attr_native_value = response_data
        self.async_write_ha_state()
