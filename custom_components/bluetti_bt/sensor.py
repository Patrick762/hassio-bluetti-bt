"""Bluetti BT sensors."""

from __future__ import annotations
from enum import Enum

import logging
from decimal import Decimal

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_NAME,
    EntityCategory,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .bluetti_bt_lib.field_attributes import FIELD_ATTRIBUTES, PACK_FIELD_ATTRIBUTES, FieldType
from .bluetti_bt_lib.utils.device_builder import build_device

from . import device_info as dev_info, get_unique_id
from .const import DATA_COORDINATOR, DOMAIN, DIAGNOSTIC_FIELDS
from .coordinator import PollingCoordinator
from .utils import unique_id_loggable

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup sensor entities."""

    device_name = entry.data.get(CONF_NAME)
    address = entry.data.get(CONF_ADDRESS)
    if address is None:
        _LOGGER.error("Device has no address")

    # Generate device info
    _LOGGER.info("Creating sensors for device with address %s", address)
    device_info = dev_info(entry)

    # Add sensors according to device_info
    bluetti_device = build_device(address, device_name)

    sensors_to_add = []
    all_fields = FIELD_ATTRIBUTES

    if len(bluetti_device.pack_polling_commands) > 0:
        # add pack fields for device
        _LOGGER.info("Device type(%s) pack_num_max(%s)", bluetti_device.type, bluetti_device.pack_num_max)
        for pack in range (1, bluetti_device.pack_num_max + 1):
            for name, field in PACK_FIELD_ATTRIBUTES(pack).items():
                all_fields.update({name+str(pack): field})

    for field_key, field_config in all_fields.items():
        if bluetti_device.has_field(field_key) or (len(bluetti_device.pack_polling_commands) > 0 and field_key.startswith("pack_")):
            category = None
            if field_config.setter is True or field_key in DIAGNOSTIC_FIELDS:
                category = EntityCategory.DIAGNOSTIC
            if field_config.type == FieldType.NUMERIC:
                sensors_to_add.append(
                    BluettiSensor(
                        hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR],
                        device_info,
                        address,
                        field_key,
                        field_config.name,
                        field_config.unit_of_measurement,
                        field_config.device_class,
                        field_config.state_class,
                        category=category,
                    )
                )
            elif field_config.type == FieldType.ENUM:
                sensors_to_add.append(
                    BluettiSensor(
                        hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR],
                        device_info,
                        address,
                        field_key,
                        field_config.name,
                        options=[o.value for o in field_config.options],
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
        name: str,
        unit_of_measurement: str | None = None,
        device_class: str | None = None,
        state_class: str | None = None,
        category: EntityCategory | None = None,
        options: list[str] | None = None,
    ):
        """Init battery entity."""
        super().__init__(coordinator)

        self._attr_has_entity_name = True
        e_name = f"{device_info.get('name')} {name}"
        self._address = address
        self._response_key = response_key
        self._unavailable_counter = 0

        self._attr_device_info = device_info
        self._attr_name = name
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

        if self.coordinator.reader.persistent_conn and not self.coordinator.reader.client.is_connected:
            return

        if self.coordinator.data is None:
            _LOGGER.debug(
                "Data from coordinator is None",
            )
            self._set_unavailable("Data is None")
            return

        _LOGGER.debug("Updating state of %s", unique_id_loggable(self._attr_unique_id))
        if not isinstance(self.coordinator.data, dict):
            _LOGGER.warning(
                "Invalid data from coordinator (sensor.%s)", unique_id_loggable(self._attr_unique_id)
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
        ):
            _LOGGER.warning(
                "Invalid response data type from coordinator (sensor.%s): %s has type %s",
                unique_id_loggable(self._attr_unique_id),
                response_data,
                type(response_data),
            )
            self._set_unavailable("Invalid data type")
            return

        self._set_available()

        # Different for enum and numeric
        if (
            self._options is not None
            and isinstance(response_data, Enum)
        ):
            # Enum
            self._attr_native_value = response_data.name
        else:
            # Numeric
            self._attr_native_value = response_data
        self.async_write_ha_state()
