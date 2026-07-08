"""Bluetti Bluetooth Integration"""

from __future__ import annotations
import asyncio
import re
import logging
from typing import List
from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.exceptions import ConfigEntryNotReady

from bluetti_bt_lib import DeviceConnection

from .utils import mac_loggable
from .const import (
    DATA_CONNECTION,
    DATA_COORDINATOR,
    DATA_LOCK,
    DOMAIN,
    MANUFACTURER,
)
from .types import FullDeviceConfig
from .coordinator import PollingCoordinator

PLATFORMS: List[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bluetti Powerstation from a config entry."""

    config = FullDeviceConfig.from_dict(entry.data)

    if config is None:
        return False

    logger = logging.getLogger(
        f"{__name__}.{mac_loggable(config.address).replace(':', '_')}"
    )

    logger.debug("Init Bluetti BT Integration")

    if not bluetooth.async_address_present(hass, config.address):
        raise ConfigEntryNotReady("Bluetti device not present")

    # Create data structure
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})

    # Create shared BLE connection, lock, and write_pending event
    lock = asyncio.Lock()
    write_pending = asyncio.Event()
    connection = DeviceConnection(
        config.address,
        use_encryption=config.use_encryption,
    )

    hass.data[DOMAIN][entry.entry_id][DATA_LOCK] = lock
    hass.data[DOMAIN][entry.entry_id][DATA_CONNECTION] = connection

    # Create coordinator for polling
    logger.debug("Creating coordinator")
    coordinator = PollingCoordinator(
        hass,
        config,
        lock,
        write_pending,
        connection,
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR] = coordinator

    logger.debug("Creating entities")
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    logger.debug("Setup done")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Bluetti Powerstation config entry."""
    connection = hass.data[DOMAIN][entry.entry_id].get(DATA_CONNECTION)
    if connection is not None:
        await connection.disconnect()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


def device_info(entry: ConfigEntry):
    """Device info."""
    config = FullDeviceConfig.from_dict(entry.data)

    if config is None:
        return None

    return DeviceInfo(
        identifiers={(DOMAIN, config.address)},
        name=entry.title,
        manufacturer=MANUFACTURER,
        model=config.dev_type,
    )


def get_unique_id(name: str, sensor_type: str | None = None):
    """Generate an unique id."""
    res = re.sub("[^A-Za-z0-9]+", "_", name).lower()
    if sensor_type is not None:
        return f"{sensor_type}.{res}"
    return res
