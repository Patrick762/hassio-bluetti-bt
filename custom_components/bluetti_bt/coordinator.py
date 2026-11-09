"""Coordinator for Bluetti integration."""

from __future__ import annotations
import asyncio
from datetime import timedelta
import logging
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from bluetti_bt_lib import (
    DeviceReader,
    DeviceReaderConfig,
    FieldName,
    build_device as library_build_device,
)
from bluetti_bt_lib.fields import DecimalArrayField, DecimalField, UIntField
from bluetti_bt_lib.registers import ReadableRegisters, WriteableRegister

from .utils import mac_loggable
from .types import FullDeviceConfig


def build_device(name: str):
    """Build a device and add the verified AC200M battery pack fields."""
    device = library_build_device(name)

    if device is None or type(device).__name__ != "AC200M":
        return device

    device.pack_fields = [
        UIntField(FieldName.PACK_SELECTED, 96),
        DecimalField(FieldName.PACK_VOLTAGE, 98, 2),
        UIntField(FieldName.PACK_BATTERY_SOC, 99),
        DecimalArrayField(FieldName.PACK_CELL_VOLTAGES, 105, 16, 2),
    ]
    device.max_packs = 2
    device.get_pack_selector = lambda pack: WriteableRegister(3006, pack)
    device.pack_polling_registers = [
        ReadableRegisters(field.address, field.size) for field in device.pack_fields
    ]

    return device


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
            logging.getLogger(
                f"{__name__}.{mac_loggable(config.address).replace(':', '_')}"
            ),
            name="Bluetti polling coordinator",
            update_interval=timedelta(seconds=config.polling_interval),
        )

        self.config = config
        self.reader = None

        # Create client
        self.logger.info("Creating client for %s", config.name)
        bluetti_device = build_device(config.name)

        if bluetti_device is None:
            self.logger.error("Device is unknown type: %s", config.name)
            return

        self.reader = DeviceReader(
            config.address,
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

        if self.reader is None:
            self.logger.error(
                "Reader not initialized - device type may be unsupported: %s",
                self.config.name,
            )
            self.last_update_success = False
            return None

        return await self.reader.read()
