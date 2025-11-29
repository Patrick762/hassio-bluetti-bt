"""Bluetti BT switches."""

from __future__ import annotations
import asyncio
import logging
import async_timeout
from bleak import BleakScanner
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from bluetti_bt_lib import build_device
from bluetti_bt_lib.base_devices import BluettiDevice
from bluetti_bt_lib.bluetooth import DeviceWriter
from bluetti_bt_lib.fields import DeviceField

from .types import FullDeviceConfig
from . import device_info as dev_info, get_unique_id
from .const import DATA_COORDINATOR, DATA_LOCK, DOMAIN
from .coordinator import PollingCoordinator
from .utils import mac_loggable, unique_id_logable

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup switch entities."""

    config = FullDeviceConfig.from_dict(entry.data)
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    lock = hass.data[DOMAIN][entry.entry_id][DATA_LOCK]

    if config is None or not isinstance(coordinator, PollingCoordinator):
        return None

    # Generate device info
    _LOGGER.info("Creating switches for device with address %s", config.address)
    device_info = dev_info(entry)

    # Add switches
    bluetti_device = build_device(config.name)

    switches_to_add = []
    switch_fields = bluetti_device.get_switch_fields()
    for field in switch_fields:
        switches_to_add.append(
            BluettiSwitch(
                bluetti_device,
                config.address,
                coordinator,
                device_info,
                field,
                lock,
            )
        )

    async_add_entities(switches_to_add)


class BluettiSwitch(CoordinatorEntity, SwitchEntity):
    """Bluetti universal switch."""

    def __init__(
        self,
        bluetti_device: BluettiDevice,
        mac: str,
        coordinator: PollingCoordinator,
        device_info: DeviceInfo,
        field: DeviceField,
        lock: asyncio.Lock,
    ):
        """Init entity."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        
        e_name = f"{device_info.get('name')} {field.name}"
        self._bluetti_device = bluetti_device
        self._mac = mac
        self._field = field
        self._response_key = field.name
        self._unavailable_counter = 5
        self._lock = lock

        self._attr_has_entity_name = True
        self._attr_device_info = device_info
        self._attr_translation_key = field.name
        self._attr_available = False
        self._attr_unique_id = get_unique_id(e_name)

        self._attr_device_class = SwitchDeviceClass.OUTLET

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._attr_available
    
    def _set_available(self):
        """Set switch as available."""
        self._attr_available = True
        self._unavailable_counter = 0
        self._attr_extra_state_attributes = {}
        self.async_write_ha_state()

    def _set_unavailable(self, cause: str = "Unknown"):
        """Set switch as unavailable."""
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
            _LOGGER.debug(
                "Invalid data from coordinator (switch.%s)",
                unique_id_logable(self._attr_unique_id),
            )
            self._set_unavailable("Invalid data")
            return

        response_data = self.coordinator.data.get(self._response_key)
        if response_data is None:
            self._set_unavailable("No data")
            return

        if not isinstance(response_data, bool):
            _LOGGER.warning(
                "Invalid response data type from coordinator (switch.%s): %s",
                unique_id_logable(self._attr_unique_id),
                response_data,
            )
            self._set_unavailable("Invalid data type")
            return

        self._set_available()
        self._attr_is_on = self.coordinator.data[self._response_key] is True
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        _LOGGER.debug(
            "Turn on %s on %s", self._response_key, mac_loggable(self._mac)
        )
        await self.write_to_device(True)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        _LOGGER.debug(
            "Turn off %s on %s", self._response_key, mac_loggable(self._mac)
        )
        await self.write_to_device(False)

    async def write_to_device(self, state: bool):
        """Write to device."""

        try:
            device = await BleakScanner.find_device_by_address(
                self._mac, timeout=5
            )

            if device is None:
                return
            
            client = await establish_connection(
                BleakClientWithServiceCache,
                device,
                device.name or "Unknown Device",
                max_attempts=10,
            )

            if not client.is_connected:
                return

            writer = DeviceWriter(
                client,
                self._bluetti_device,
                lock=self._lock
            )

            async with async_timeout.timeout(15):
                # Send command
                await writer.write(self._field.name, state)

                # Wait until device has changed value, otherwise reading register might reset it
                await asyncio.sleep(5)

        except TimeoutError:
            _LOGGER.error("Timed out for device %s", mac_loggable(self._mac))
            return None

        await self.coordinator.async_request_refresh()
