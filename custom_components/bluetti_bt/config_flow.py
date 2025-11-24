"""Bluetti Bluetooth Config Flow"""

from __future__ import annotations
import re
import logging
from typing import Any
from bleak import BleakClient
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.const import CONF_ADDRESS
from homeassistant.data_entry_flow import FlowResult
from bluetti_bt_lib import recognize_device

from .types import InitialDeviceConfig, ManufacturerData, OptionalDeviceConfig
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class BluettiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Bluetti BT devices."""

    def __init__(self) -> None:
        _LOGGER.info("Initialize config flow")
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle bluetooth discovery."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        # Get device type
        client = BleakClient(discovery_info.device)
        recognized = await recognize_device(client, self.hass.loop.create_future)

        if recognized is None:
            return await self.async_abort(reason="Device type not supported")

        _LOGGER.info(
            "Device identified as %s with iot module version %s (using encryption: %s)",
            recognized.name + "1",  # TODO add serial to name
            recognized.iot_version,
            recognized.encrypted,
        )

        discovery_info.manufacturer_data = ManufacturerData(
            recognized.name, recognized.encrypted
        ).as_dict
        discovery_info.name = recognized.name
        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {"name": discovery_info.name}
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle user input."""

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            discovery_info = self._discovered_devices[address]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            name = re.sub("[^A-Z0-9]+", "", discovery_info.name)

            manufacturer_data = ManufacturerData.from_dict(
                discovery_info.manufacturer_data
            )

            data = InitialDeviceConfig(
                discovery_info.address,
                name,
                manufacturer_data.dev_type,
                manufacturer_data.use_encryption,
            )

            return self.async_create_entry(
                title=name,
                data=data.as_dict,
            )

        if discovery := self._discovery_info:
            self._discovered_devices[discovery.address] = discovery
        else:
            current_addresses = self._async_current_ids()
            for discovery in async_discovered_service_info(self.hass):
                address = discovery.address
                if address in current_addresses or address in self._discovered_devices:
                    continue
                self._discovered_devices[discovery.address] = discovery

        if not self._discovered_devices:
            return self.async_abort(reason="no_unconfigured_devices")

        data_schema = vol.Schema(
            {
                vol.Required(CONF_ADDRESS): vol.In(
                    {
                        service_info.address: service_info.name
                        for service_info in self._discovered_devices.values()
                    }
                ),
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        super().__init__()
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            config = OptionalDeviceConfig.from_dict(user_input)

            reason = config.validate()

            if reason is not None:
                return self.async_abort(reason=reason)

            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    **self.config_entry.data,
                    **config.as_dict,
                },
            )
            return self.async_create_entry(
                title="",
                data=config.as_dict,
            )

        defaults = OptionalDeviceConfig.from_dict({})

        return self.async_show_form(
            step_id="init",
            data_schema=defaults.schema,
        )
