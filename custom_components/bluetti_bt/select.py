"""Bluetti BT selects."""

from __future__ import annotations
import asyncio
import logging
import async_timeout
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from bluetti_bt_lib import build_device, BluettiDevice, DeviceConnection, DeviceWriter, DeviceWriterConfig, FieldName
from bluetti_bt_lib.fields import SelectField

from .types import FullDeviceConfig, get_category
from . import device_info as dev_info, get_unique_id
from .const import DATA_CONNECTION, DATA_COORDINATOR, DATA_LOCK, DOMAIN
from .coordinator import PollingCoordinator
from .utils import mac_loggable, unique_id_logable


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup select entities."""

    config = FullDeviceConfig.from_dict(entry.data)
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    lock = hass.data[DOMAIN][entry.entry_id][DATA_LOCK]
    connection = hass.data[DOMAIN][entry.entry_id][DATA_CONNECTION]

    logger = logging.getLogger(
        f"{__name__}.{mac_loggable(config.address).replace(':', '_')}"
    )

    if config is None or not isinstance(coordinator, PollingCoordinator):
        logger.error("No coordinator found")
        return None

    # Generate device info
    logger.info("Creating selects for device with address %s", config.address)
    device_info = dev_info(entry)

    # Add selects
    bluetti_device = build_device(config.name)

    selects_to_add = []
    select_fields = bluetti_device.get_select_fields()
    for field in select_fields:
        category = get_category(FieldName(field.name))

        selects_to_add.append(
            BluettiSelect(
                bluetti_device,
                config.address,
                config.use_encryption,
                coordinator,
                device_info,
                field,
                lock,
                connection,
                category=category,
                logger=logger,
            )
        )

    async_add_entities(selects_to_add)


class BluettiSelect(CoordinatorEntity, SelectEntity):
    """Bluetti universal select."""

    def __init__(
        self,
        bluetti_device: BluettiDevice,
        address: str,
        use_encryption: bool,
        coordinator: PollingCoordinator,
        device_info: DeviceInfo,
        field: SelectField,
        lock: asyncio.Lock,
        connection: DeviceConnection,
        category: EntityCategory | None = None,
        logger: logging.Logger = logging.getLogger(),
    ) -> None:
        """Init entity."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._logger = logger

        e_name = f"{device_info.get('name')} {field.name}"
        self._bluetti_device = bluetti_device
        self._address = address
        self._use_encryption = use_encryption
        self._field = field
        self._response_key = field.name
        self._unavailable_counter = 5
        self._lock = lock
        self._connection = connection
        self._attr_options = [e.name for e in field.e]

        self._attr_has_entity_name = True
        self._attr_device_info = device_info
        self._attr_translation_key = field.name
        self._attr_available = False
        self._attr_unique_id = get_unique_id(e_name)
        self._attr_entity_category = category

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._attr_available

    def _set_available(self):
        """Set select as available."""
        self._attr_available = True
        self._unavailable_counter = 0
        self._attr_extra_state_attributes = {}
        self.async_write_ha_state()

    def _set_unavailable(self, cause: str = "Unknown"):
        """Set select as unavailable."""
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

        if self.coordinator.write_pending.is_set():
            return

        if self.coordinator.data is None:
            self._logger.debug(
                "Data from coordinator is None",
            )
            self._set_unavailable("Data is None")
            return

        self._logger.debug(
            "Updating state of %s", unique_id_logable(self._attr_unique_id)
        )
        if not isinstance(self.coordinator.data, dict):
            self._logger.debug(
                "Invalid data from coordinator (select.%s)",
                unique_id_logable(self._attr_unique_id),
            )
            self._set_unavailable("Invalid data")
            return

        response_data = self.coordinator.data.get(self._response_key)
        if response_data is None:
            self._set_unavailable("No data")
            return

        if not isinstance(response_data, self._field.e):
            self._logger.warning(
                "Invalid response data type from coordinator (select.%s): %s",
                unique_id_logable(self._attr_unique_id),
                response_data,
            )
            self._set_unavailable("Invalid data type")
            return

        self._set_available()
        self.current_option = response_data.name
        self.async_write_ha_state()

    async def async_select_option(self, option: str):
        """Set the entity to value."""
        self._logger.debug(
            "Set %s on %s to %s",
            self._response_key,
            mac_loggable(self._address),
            option,
        )
        await self.write_to_device(option)

    async def write_to_device(self, state: str) -> None:
        """Write a string value to the device field."""
        # Update UI immediately — don't wait for coordinator confirmation
        self.current_option = state
        self.async_write_ha_state()

        self.coordinator.write_pending.set()
        try:
            async with async_timeout.timeout(60):
                writer = self._create_writer()
                await writer.write(self._field.name, state)
                await asyncio.sleep(1)
        except TimeoutError:
            self._logger.error("Timed out for device %s", mac_loggable(self._address))
        finally:
            self.coordinator.write_pending.clear()
            await self.coordinator.async_request_refresh()

    def _create_writer(self) -> DeviceWriter:
        """Build a DeviceWriter that uses the shared persistent connection."""
        return DeviceWriter(
            bleak_client=None,
            bluetti_device=self._bluetti_device,
            config=DeviceWriterConfig(timeout=30, use_encryption=self._use_encryption),
            lock=self._lock,
            connection=self._connection,
        )
