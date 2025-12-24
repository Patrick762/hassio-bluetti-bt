"""Bluetti Bluetooth Config Flow"""

from __future__ import annotations
import re
import logging
from typing import Any
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
        recognized = await recognize_device(
            discovery_info.address, self.hass.loop.create_future
        )

        if recognized is None:
            return self.async_abort(reason="Device type not supported")

        _LOGGER.info(
            "Device identified as %s with iot module version %s (using encryption: %s)",
            recognized.name,
            recognized.iot_version,
            recognized.encrypted,
        )

        discovery_info.manufacturer_data = ManufacturerData(
            recognized.name, recognized.encrypted
        ).as_dict
        discovery_info.name = recognized.full_name
        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {"name": discovery_info.name}
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle user input."""

        # Handle click on "OK" button
        if user_input is not None:
            discovery_info = self._discovery_info
            address = discovery_info.address
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            name = re.sub("[^A-Z0-9]+", "", discovery_info.name)

            manufacturer_data = ManufacturerData.from_dict(
                discovery_info.manufacturer_data
            )

            data = InitialDeviceConfig(
                address,
                name,
                manufacturer_data.dev_type,
                manufacturer_data.use_encryption,
            )

            optional = OptionalDeviceConfig.from_dict({})

            return self.async_create_entry(
                title=name,
                data={
                    **data.as_dict,
                    **optional.as_dict,
                },
            )

        if not self._discovery_info:
            return self.async_abort(reason="no_unconfigured_devices")

        # The input from this is not used, we use the discovered and known working address
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_ADDRESS,
                    default=self._discovery_info.address,
                ): str,
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        )

    @staticmethod
    def async_get_options_flow(_) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow."""

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

        defaults = OptionalDeviceConfig.from_dict(self.config_entry.data)

        return self.async_show_form(
            step_id="init",
            data_schema=defaults.schema,
        )
