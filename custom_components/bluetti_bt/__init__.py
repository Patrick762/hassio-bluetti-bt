"""Bluetti Bluetooth Integration"""

from __future__ import annotations

import re
import logging
from typing import List

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_TYPE, CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_MAX_RETRIES,
    CONF_PERSISTENT_CONN,
    CONF_POLLING_INTERVAL,
    CONF_POLLING_TIMEOUT,
    CONF_USE_CONTROLS,
    DATA_COORDINATOR,
    DATA_POLLING_RUNNING,
    DOMAIN,
    MANUFACTURER,
)
from .coordinator import PollingCoordinator

PLATFORMS: List[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bluetti Powerstation from a config entry."""

    _LOGGER.debug("Init Bluetti BT Integration")

    address = entry.data.get(CONF_ADDRESS)
    device_name = entry.data.get(CONF_NAME)
    use_controls = entry.data.get(CONF_USE_CONTROLS)
    polling_interval = entry.data.get(CONF_POLLING_INTERVAL, 60)
    persistent_conn = entry.data.get(CONF_PERSISTENT_CONN, False)
    polling_timeout = entry.data.get(CONF_POLLING_TIMEOUT, 120)
    max_retries = entry.data.get(CONF_MAX_RETRIES, 5)

    if address is None:
        return False

    if not bluetooth.async_address_present(hass, address):
        raise ConfigEntryNotReady("Bluetti device not present")

    # Create data structure
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})
    hass.data[DOMAIN][entry.entry_id].setdefault(DATA_POLLING_RUNNING, False)

    # Create coordinator for polling
    _LOGGER.debug("Creating coordinator")
    coordinator = PollingCoordinator(hass, address, device_name, polling_interval, persistent_conn, polling_timeout, max_retries)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id].setdefault(DATA_COORDINATOR, coordinator)

    _LOGGER.debug("Creating entities")
    platforms: list = PLATFORMS
    if use_controls is True:
        _LOGGER.warning("You are using controls with this integration at your own risk!")
        platforms.append(Platform.SWITCH)

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    _LOGGER.debug("Setup done")

    return True


def device_info(entry: ConfigEntry) -> DeviceInfo:
    """Device info."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.data.get(CONF_ADDRESS))},
        name=entry.title,
        manufacturer=MANUFACTURER,
        model=entry.data.get(CONF_TYPE),
    )


def get_unique_id(name: str, sensor_type: str | None = None):
    """Generate an unique id."""
    res = re.sub("[^A-Za-z0-9]+", "_", name).lower()
    if sensor_type is not None:
        return f"{sensor_type}.{res}"
    return res
