"""Bluetti BT switches."""

from __future__ import annotations

import asyncio
import logging
import async_timeout

from bleak import BleakError

from homeassistant.components import bluetooth
from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_NAME,
    EntityCategory,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .bluetti_bt_lib.base_devices.BluettiDevice import BluettiDevice
from .bluetti_bt_lib.const import WRITE_UUID
from .bluetti_bt_lib.field_attributes import FIELD_ATTRIBUTES, PACK_FIELD_ATTRIBUTES, FieldType
from .bluetti_bt_lib.utils.device_builder import build_device

from . import device_info as dev_info, get_unique_id
from .const import CONTROL_FIELDS, DATA_COORDINATOR, DOMAIN
from .coordinator import PollingCoordinator
from .utils import mac_loggable, unique_id_loggable

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup switch entities."""

    device_name = entry.data.get(CONF_NAME)
    address = entry.data.get(CONF_ADDRESS)
    if address is None:
        _LOGGER.error("Device has no address")

    # Generate device info
    _LOGGER.info("Creating switches for device with address %s", address)
    device_info = dev_info(entry)

    # Add sensors according to device_info
    bluetti_device = build_device(address, device_name)

    sensors_to_add = []
    all_fields = FIELD_ATTRIBUTES
    for field_key, field_config in all_fields.items():
        if bluetti_device.has_field(field_key):
            if field_config.type == FieldType.BOOL:
                if field_config.setter is True and field_key in CONTROL_FIELDS:
                    sensors_to_add.append(
                        BluettiSwitch(
                            bluetti_device,
                            hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR],
                            device_info,
                            address,
                            field_key,
                            field_config.name,
                            entry.entry_id
                        )
                    )

    async_add_entities(sensors_to_add)


class BluettiSwitch(CoordinatorEntity, SwitchEntity):
    """Bluetti universal switch."""

    def __init__(
        self,
        bluetti_device: BluettiDevice,
        coordinator: PollingCoordinator,
        device_info: DeviceInfo,
        address,
        response_key: str,
        name: str,
        entry_id: str,
        category: EntityCategory | None = None,
    ):
        """Init entity."""
        super().__init__(coordinator)

        self._bluetti_device = bluetti_device
        self._coordinator = coordinator
        self._client = coordinator.reader.client
        self._polling_lock = coordinator.reader.polling_lock
        e_name = f"{device_info.get('name')} {name}"
        self._address = address
        self._response_key = response_key
        self._entry_id = entry_id

        self._attr_device_info = device_info
        self._attr_has_entity_name = True
        self._attr_name = name
        self._attr_available = False
        self._attr_unique_id = get_unique_id(e_name)
        self._attr_entity_category = category
        self._attr_device_class = SwitchDeviceClass.OUTLET

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._attr_available

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.reader.persistent_conn and not self.coordinator.reader.client.is_connected:
            return

        _LOGGER.debug("Updating state of %s", unique_id_loggable(self._attr_unique_id))
        if not isinstance(self.coordinator.data, dict):
            _LOGGER.debug(
                "Invalid data from coordinator (switch.%s)", unique_id_loggable(self._attr_unique_id)
            )
            self._attr_available = False
            self.async_write_ha_state()
            return

        response_data = self.coordinator.data.get(self._response_key)
        if response_data is None:
            self._attr_available = False
            self.async_write_ha_state()
            return

        if not isinstance(response_data, bool):
            _LOGGER.warning(
                "Invalid response data type from coordinator (switch.%s): %s",
                unique_id_loggable(self._attr_unique_id),
                response_data,
            )
            self._attr_available = False
            self.async_write_ha_state()
            return

        self._attr_available = True
        self._attr_is_on = self.coordinator.data[self._response_key] is True
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        _LOGGER.debug("Turn on %s on %s", self._response_key, mac_loggable(self._address))
        await self.write_to_device(True)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        _LOGGER.debug("Turn off %s on %s", self._response_key, mac_loggable(self._address))
        await self.write_to_device(False)

    async def write_to_device(self, state: bool):
        """Write to device."""
        command = self._bluetti_device.build_setter_command(self._response_key, state)

        async with self._polling_lock:
            try:
                async with async_timeout.timeout(15):
                    if not self._client.is_connected:
                        await self._client.connect()

                    # Send command
                    _LOGGER.debug("Requesting %s (%s,%s)", command, self._response_key, state)
                    await self._client.write_gatt_char(
                        WRITE_UUID, bytes(command)
                    )

                    # Wait until device has changed value, otherwise reading register might reset it
                    await asyncio.sleep(5)

            except TimeoutError:
                _LOGGER.error("Timed out for device %s", mac_loggable(self._address))
                return None
            except BleakError as err:
                _LOGGER.error("Bleak error: %s", err)
                return None
            finally:
                # Disconnect if connection not persistant
                if not self._coordinator.reader.persistent_conn:
                    await self._client.disconnect()

        await self.coordinator.async_request_refresh()
