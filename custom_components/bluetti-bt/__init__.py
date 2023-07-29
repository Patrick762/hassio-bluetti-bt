"""Bluetti Bluetooth Integration"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)
PLATFORMS: [Platform] = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bluetti Powerstation from a config entry."""

    address = entry.data.get(CONF_ADDRESS)
    
    if address is None:
        return False

    _LOGGER.error(f"Device address: {address}")
    return True
