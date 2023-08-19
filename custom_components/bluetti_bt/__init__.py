"""Bluetti Bluetooth Integration"""

from __future__ import annotations

import re
import logging

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_TYPE, CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DATA_COORDINATOR, DOMAIN, MANUFACTURER, CONF_USE_CONTROLS, DATA_POLLING_RUNNING
from .coordinator import PollingCoordinator

PLATFORMS: [Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bluetti Powerstation from a config entry."""

    address = entry.data.get(CONF_ADDRESS)
    device_name = entry.data.get(CONF_NAME)
    use_controls = entry.data.get(CONF_USE_CONTROLS)

    if address is None:
        return False

    if not bluetooth.async_address_present(hass, address):
        raise ConfigEntryNotReady("Bluetti device not present")

    # Create data structure
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(entry.entry_id, {})
    hass.data[DOMAIN][entry.entry_id].setdefault(DATA_POLLING_RUNNING, False)

    # Create coordinator for polling
    coordinator = PollingCoordinator(hass, address, device_name)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id].setdefault(DATA_COORDINATOR, coordinator)

    platforms: list = PLATFORMS
    if use_controls is True:
        _LOGGER.warning("You are using controls with this integration at your own risk!")
        platforms.append(Platform.SWITCH)

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, platforms)

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
