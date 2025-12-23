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

from .const import (
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
]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bluetti Powerstation from a config entry."""

    _LOGGER.debug("Init Bluetti BT Integration")

    config = FullDeviceConfig.from_dict(entry.data)

    if config is None:
        return False

    if not bluetooth.async_address_present(hass, config.address):
        raise ConfigEntryNotReady("Bluetti device not present")

    # Create data structure
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})

    # Create lock
    lock = asyncio.Lock()

    # Create coordinator for polling
    _LOGGER.debug("Creating coordinator")
    coordinator = PollingCoordinator(
        hass,
        config,
        lock,
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id].setdefault(DATA_COORDINATOR, coordinator)
    hass.data[DOMAIN][entry.entry_id].setdefault(DATA_LOCK, lock)

    _LOGGER.debug("Creating entities")
    platforms: list = PLATFORMS
    if not config.use_encryption:
        platforms.append(Platform.SWITCH)
        platforms.append(Platform.SELECT)

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    _LOGGER.debug("Setup done")

    return True


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
