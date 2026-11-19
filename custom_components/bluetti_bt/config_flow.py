"""Bluetti Bluetooth Config Flow"""

from __future__ import annotations
import re
import logging
from typing import Any
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
)
from homeassistant.const import CONF_ADDRESS
from homeassistant.data_entry_flow import FlowResult
from bluetti_bt_lib import build_device, recognize_device
from bluetti_bt_lib.devices import DEVICES, DEVICE_NAME_RE

from .types import InitialDeviceConfig, ManufacturerData, OptionalDeviceConfig
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONF_TYPE = "type"
CONF_SERIAL = "serial"
CONF_USE_ENCRYPTION = "use_encryption"

MAC_RE = re.compile(r"^([0-9A-F]{2}:){5}[0-9A-F]{2}$")


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
            # Recognition can fail even for supported devices, e.g. when the
            # encryption handshake does not finish within the library's fixed
            # timeout over an ESPHome Bluetooth proxy. Let the user confirm the
            # device details manually instead of aborting.
            _LOGGER.warning(
                "Could not identify device %s automatically, asking for manual setup",
                discovery_info.name,
            )
            self._discovery_info = discovery_info
            self.context["title_placeholders"] = {"name": discovery_info.name}
            return await self.async_step_manual()

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
            return await self.async_step_manual()

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

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Set up a device by entering its details manually."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS].strip().upper()
            dev_type = user_input[CONF_TYPE]
            serial = re.sub(r"\s+", "", user_input[CONF_SERIAL])
            use_encryption = user_input[CONF_USE_ENCRYPTION]
            name = dev_type + serial

            if MAC_RE.match(address) is None:
                errors[CONF_ADDRESS] = "invalid_address"
            elif not serial.isdigit():
                errors[CONF_SERIAL] = "invalid_serial"
            elif build_device(name) is None:
                errors[CONF_TYPE] = "unsupported_type"
            else:
                await self.async_set_unique_id(address, raise_on_progress=False)
                self._abort_if_unique_id_configured()

                data = InitialDeviceConfig(address, name, dev_type, use_encryption)
                optional = OptionalDeviceConfig.from_dict({})

                return self.async_create_entry(
                    title=name,
                    data={
                        **data.as_dict,
                        **optional.as_dict,
                    },
                )

        defaults = user_input or self._manual_defaults()

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_ADDRESS, default=defaults.get(CONF_ADDRESS, "")
                ): str,
                vol.Required(
                    CONF_TYPE, default=defaults.get(CONF_TYPE, vol.UNDEFINED)
                ): vol.In(sorted(DEVICES.keys())),
                vol.Required(
                    CONF_SERIAL, default=defaults.get(CONF_SERIAL, "")
                ): str,
                vol.Required(
                    CONF_USE_ENCRYPTION,
                    default=defaults.get(CONF_USE_ENCRYPTION, False),
                ): bool,
            }
        )
        return self.async_show_form(
            step_id="manual",
            data_schema=data_schema,
            errors=errors,
        )

    def _manual_defaults(self) -> dict[str, Any]:
        """Prefill the manual form from the bluetooth discovery, if any."""
        if self._discovery_info is None:
            return {}

        defaults: dict[str, Any] = {CONF_ADDRESS: self._discovery_info.address}

        match = DEVICE_NAME_RE.match(self._discovery_info.name or "")
        if match is not None and match[1] in DEVICES:
            defaults[CONF_TYPE] = match[1]
            defaults[CONF_SERIAL] = match[2]

        return defaults

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
