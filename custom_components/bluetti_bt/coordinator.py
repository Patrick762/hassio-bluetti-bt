"""Coordinator for Bluetti integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from bleak import BleakClient

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .bluetti_bt_lib.bluetooth.device_reader import DeviceReader
from .bluetti_bt_lib.utils.device_builder import build_device

from .utils import mac_loggable

_LOGGER = logging.getLogger(__name__)


class PollingCoordinator(DataUpdateCoordinator):
    """Polling coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        address: str,
        device_name: str,
        polling_interval: int,
        persistent_conn: bool,
        polling_timeout: int,
        max_retries: int,
    ):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Bluetti polling coordinator",
            update_interval=timedelta(seconds=polling_interval),
        )

        self.address = address

        # Create client
        self.logger.debug("Creating client")
        device = bluetooth.async_ble_device_from_address(hass, address)
        if device is None:
            self.logger.error("Device %s not available", mac_loggable(address))
            return None
        client = BleakClient(device)
        bluetti_device = build_device(address, device_name)
        if bluetti_device is None:
            self.logger.error("Failed to build device %s with name %s", mac_loggable(address), device_name)
            return None

        self.reader = DeviceReader(
            client,
            bluetti_device,
            self.hass.loop.create_future,
            persistent_conn=persistent_conn,
            polling_timeout=polling_timeout,
            max_retries=max_retries,
            device_address=address,
            ble_device=device,
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """

        # Presence check (best-effort). With BLE proxies this may flap; proceed anyway.
        if bluetooth.async_address_present(self.hass, self.address) is False:
            self.logger.debug("Device address %s currently not present in scanner; attempting read anyway", mac_loggable(self.address))

        return await self.reader.read_data()
