"""Coordinator for Bluetti integration."""

from __future__ import annotations
import asyncio
from datetime import timedelta
import logging
from bleak import BleakClient
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from bluetti_bt_lib import build_device, DeviceReader, DeviceReaderConfig

from .types import FullDeviceConfig
from .utils import mac_loggable

_LOGGER = logging.getLogger(__name__)


class PollingCoordinator(DataUpdateCoordinator):
    """Polling coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: FullDeviceConfig,
        lock: asyncio.Lock,
    ):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Bluetti polling coordinator",
            update_interval=timedelta(seconds=config.polling_interval),
        )

        self.config = config

        # Create client
        self.logger.info("Creating client for %s", config.name)
        device = bluetooth.async_ble_device_from_address(hass, config.address)
        if device is None:
            self.logger.error("Device %s not available", mac_loggable(config.address))
            return None
        client = BleakClient(device)
        bluetti_device = build_device(config.name)

        if bluetti_device is None:
            self.logger.error("Device is unknown type")
            return None

        self.reader = DeviceReader(
            client,
            bluetti_device,
            self.hass.loop.create_future,
            DeviceReaderConfig(
                config.polling_timeout,
                config.use_encryption,
            ),
            lock,
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """

        # Check if device is connected
        if (
            bluetooth.async_address_present(
                self.hass, self.config.address, connectable=True
            )
            is False
        ):
            self.logger.warning("Device not connected")
            self.last_update_success = False
            return None

        return await self.reader.read()
