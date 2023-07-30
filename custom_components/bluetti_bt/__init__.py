"""Bluetti Bluetooth Integration"""

from __future__ import annotations

import re
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)
PLATFORMS: [Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bluetti Powerstation from a config entry."""

    address = entry.data.get(CONF_ADDRESS)

    if address is None:
        return False

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.error("Device address: %s", address)
    return True


def device_info(entry: ConfigEntry) -> DeviceInfo:
    """Device info."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.data.get(CONF_ADDRESS))},
        name=entry.title,
        manufacturer=MANUFACTURER,
        model=get_type_by_bt_name(entry.title),
    )


def get_unique_id(name: str, sensor_type: str | None = None):
    """Generate an unique id."""
    res = re.sub("[^A-Za-z0-9]+", "_", name).lower()
    if sensor_type is not None:
        return f"{sensor_type}.{res}"
    return res


def get_type_by_bt_name(bt_name: str):
    """Get the device type."""
    dev_type = "Unknown"
    if bt_name.startswith("AC200M"):
        dev_type = "AC200M"
    elif bt_name.startswith("AC300"):
        dev_type = "AC300"
    elif bt_name.startswith("AC500"):
        dev_type = "AC500"
    elif bt_name.startswith("AC60"):
        dev_type = "AC60"
    elif bt_name.startswith("EB3A"):
        dev_type = "EB3A"
    elif bt_name.startswith("EP500"):
        dev_type = "EP500"
    elif bt_name.startswith("EP600"):
        dev_type = "EP600"
    return dev_type
