"""Bluetti BT sensors."""

from __future__ import annotations

from datetime import timedelta
import logging

import async_timeout

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import CONF_ADDRESS
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from . import device_info as dev_info, get_unique_id

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup sensor entities."""

    # Create coordinator for polling
    coordinator = PollingCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    # Generate device info
    _LOGGER.error("Creating sensors for device %s", entry.data.get(CONF_ADDRESS))
    device_info = dev_info(entry)
    async_add_entities(Battery(coordinator, device_info))


class PollingCoordinator(DataUpdateCoordinator):
    """Polling coordinator."""

    def __init__(self, hass):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Bluetti polling coordinator",
            update_interval=timedelta(seconds=10),
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        self.logger.error("Polling data")


class Battery(CoordinatorEntity, SensorEntity):
    """Bluetti battery."""

    def __init__(self, coordinator: PollingCoordinator, device_info: DeviceInfo):
        """Init battery entity."""
        super().__init__(coordinator)

        self._attr_device_info = device_info
        self._attr_name = f"{device_info.get('name')} Battery level"
        self._attr_unique_id = get_unique_id(f"{device_info.get('name')} Battery level")
        self._attr_unit_of_measurement = "%"
        self._attr_device_class = "battery"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.error("Updating state of %s", self._attr_unique_id)
        self.async_write_ha_state()
