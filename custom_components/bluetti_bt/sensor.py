"""Bluetti BT sensors."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from bleak import BleakClient

from homeassistant.components import bluetooth
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import CONF_ADDRESS
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from bluetti_mqtt.bluetooth.client import BluetoothClient

from . import device_info as dev_info, get_unique_id

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup sensor entities."""

    address = entry.data.get(CONF_ADDRESS)
    if address is None:
        _LOGGER.error("Device has no address")

    # Create coordinator for polling
    coordinator = PollingCoordinator(hass, address)
    await coordinator.async_config_entry_first_refresh()

    # Generate device info
    _LOGGER.info("Creating sensors for device with address %s", address)
    device_info = dev_info(entry)
    async_add_entities([Battery(coordinator, device_info, address)])


class PollingCoordinator(DataUpdateCoordinator):
    """Polling coordinator."""

    def __init__(self, hass: HomeAssistant, address):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Bluetti polling coordinator",
            update_interval=timedelta(seconds=10),
        )
        self._address = address
        self.notify_future = None
        self.command_queue = asyncio.Queue()
        self.notify_response = bytearray()

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        self.logger.error("Polling data")

        device = bluetooth.async_ble_device_from_address(self.hass, self._address)
        if device is None:
            self.logger.error("Device not available")
            return

        self.logger.error("BT RSSI to device %s: %s", self._address, device.rssi)

        # Proceed with bluetti_mqtt parts

        # TODO: Fill command_queue

        client = BleakClient(device)

        try:
            client.connect()
            await client.start_notify(
                BluetoothClient.NOTIFY_UUID, self._notification_handler
            )

            while not self.command_queue.empty():
                try:
                    # Prepare to make request
                    current_command, cmd_future = self.command_queue.get()
                    self.notify_future = self.hass.loop.create_future()
                    self.notify_response = bytearray()

                    # Make request
                    await client.write_gatt_char(
                        BluetoothClient.WRITE_UUID, bytes(current_command)
                    )

                    # Wait for response
                    res = await asyncio.wait_for(
                        self.notify_future, timeout=BluetoothClient.RESPONSE_TIMEOUT
                    )
                    if cmd_future:
                        cmd_future.set_result(res)
                except:
                    self.logger.error("Error polling data")

        finally:
            client.disconnect()

    def _notification_handler(self, _sender: int, data: bytearray):
        """Handle bt data."""
        self.logger.error("Data received: ", data.decode())


class Battery(CoordinatorEntity, SensorEntity):
    """Bluetti battery."""

    def __init__(
        self, coordinator: PollingCoordinator, device_info: DeviceInfo, address
    ):
        """Init battery entity."""
        super().__init__(coordinator)
        self._attr_device_info = device_info
        self._attr_name = f"{device_info.get('name')} Battery level"
        self._attr_unique_id = get_unique_id(f"{device_info.get('name')} Battery level")
        self._attr_unit_of_measurement = "%"
        self._attr_device_class = "battery"
        self._address = address

    @property
    def available(self) -> bool:
        if self._address is None:
            return False
        return bluetooth.async_address_present(self.hass, self._address)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.error("Updating state of %s", self._attr_unique_id)
        self.async_write_ha_state()
