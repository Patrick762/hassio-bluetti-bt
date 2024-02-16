"""Coordinator for Bluetti integration."""

from __future__ import annotations
from typing import cast

import asyncio
from datetime import timedelta
import logging
import async_timeout

from bleak import BleakClient, BleakError

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .bluetti_bt_lib.const import NOTIFY_UUID, RESPONSE_TIMEOUT, WRITE_UUID
from .bluetti_bt_lib.exceptions import BadConnectionError, ModbusError, ParseError
from .bluetti_bt_lib.utils.commands import ReadHoldingRegisters

from .const import DATA_POLLING_RUNNING, DOMAIN
from .utils import mac_loggable, build_device

_LOGGER = logging.getLogger(__name__)


class PollingCoordinator(DataUpdateCoordinator):
    """Polling coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        address: str,
        device_name: str,
        polling_interval: int,
        persistent_conn: bool,
        polling_timeout: int,
        max_retries: int,
    ):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Bluetti polling coordinator",
            update_interval=timedelta(seconds=polling_interval),
        )
        self._address = address
        self.has_notifier = False
        self.notify_future = None
        self.current_command = None
        self.notify_response = bytearray()
        self.bluetti_device = build_device(address, device_name)
        self.persistent_conn = persistent_conn
        self.polling_timeout = polling_timeout
        self.max_retries = max_retries

        # Create client
        self.logger.debug("Creating client")
        device = bluetooth.async_ble_device_from_address(hass, address)
        if device is None:
            self.logger.error("Device %s not available", mac_loggable(address))
            return None
        self.client = BleakClient(device)

        # polling mutex to guard against switches
        self.polling_lock = asyncio.Lock()

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        self.hass.data[DOMAIN][self.config_entry.entry_id][DATA_POLLING_RUNNING] = True

        self.logger.debug("Polling data")

        if self.bluetti_device is None:
            self.logger.error("Device type for %s not found", mac_loggable(self._address))
            return None

        parsed_data: dict = {}

        async with self.polling_lock:
            try:
                async with async_timeout.timeout(self.polling_timeout):

                    # Reconnect if not connected
                    for attempt in range(1, self.max_retries + 1):
                        try:
                            if not self.client.is_connected:
                                await self.client.connect()
                            break
                        except Exception as e:
                            if attempt == self.max_retries or attempt == 1:
                                raise  # pass exception on max_retries attempt
                            else:
                                self.logger.warning(f"Connect unsucessful (attempt {attempt}): {e}. Retrying...")
                                await asyncio.sleep(2)

                    # Attach notifier if needed
                    if not self.has_notifier:
                        await self.client.start_notify(
                            NOTIFY_UUID, self._notification_handler
                        )
                        self.has_notifier = True

                    for command in self.bluetti_device.polling_commands:
                        try:
                            body = command.parse_response(
                                await self.async_send_command(command)
                            )
                            self.logger.debug("Raw data: %s", body)
                            parsed = self.bluetti_device.parse(
                                command.starting_address, body
                            )
                            self.logger.debug("Parsed data: %s", parsed)
                            parsed_data.update(parsed)

                        except ParseError:
                            self.logger.warning("Got a parse exception...")

                    if len(self.bluetti_device.pack_polling_commands) > 0:
                        self.logger.debug("Polling battery packs")
                        # pack polling
                        for pack in range (1, self.bluetti_device.pack_num_max + 1):
                            # Set current pack number
                            await self.async_send_command(
                                self.bluetti_device.build_setter_command('pack_num', pack)
                            )

                            # We need to wait after switching packs for the data to be available
                            await asyncio.sleep(5)

                            for command in self.bluetti_device.pack_polling_commands:
                                # Request & parse result for each pack
                                try:
                                    body = command.parse_response(
                                        await self.async_send_command(command)
                                    )
                                    parsed = self.bluetti_device.parse(
                                        command.starting_address, body
                                    )
                                    self.logger.debug("Parsed data: %s", parsed)

                                    pack_number = parsed.get('pack_num')
                                    if not isinstance(pack_number, int) or pack_number != pack:
                                        self.logger.debug("Parsed pack_num(%s) does not match expected '%s'", pack_number, pack)
                                        continue

                                    for key, value in parsed.items():
                                        parsed_data.update({key+str(pack):value})

                                except ParseError:
                                    self.logger.warning("Got a parse exception...")

            except TimeoutError:
                self.logger.warning("Polling timed out for device %s", mac_loggable(self._address))
                return None
            except BleakError as err:
                self.logger.warning("Bleak error: %s", err)
                return None
            finally:
                # Disconnect if connection not persistant
                if not self.persistent_conn:
                    if self.has_notifier:
                        await self.client.stop_notify(NOTIFY_UUID)
                        self.has_notifier = False
                    await self.client.disconnect()

            self.hass.data[DOMAIN][self.config_entry.entry_id][DATA_POLLING_RUNNING] = False

            # Pass data back to sensors
            return parsed_data

    async def async_send_command(self, command: ReadHoldingRegisters) -> bytes:
        """Send command and return response"""
        try:
            # Prepare to make request
            self.current_command = command
            self.notify_future = self.hass.loop.create_future()
            self.notify_response = bytearray()

            # Make request
            self.logger.debug("Requesting %s", command)
            await self.client.write_gatt_char(
                WRITE_UUID, bytes(command)
            )

            # Wait for response
            res = await asyncio.wait_for(
                self.notify_future, timeout=RESPONSE_TIMEOUT
            )

            # Process data
            self.logger.debug("Got %s bytes", len(res))
            return cast(bytes, res)

        except TimeoutError:
            self.logger.debug(
                "Polling timed out (address: %s)", mac_loggable(self._address)
            )
        except ModbusError as err:
            self.logger.warning(
                "Got an invalid request error for %s: %s",
                command,
                err,
            )
        except (BadConnectionError, BleakError) as err:
            self.logger.warning(
                "Needed to disconnect due to error: %s (This can also be the case if you used device controls)", err
            )

        # caught an exception, return empty bytes object
        return bytes()

    def _notification_handler(self, _sender: int, data: bytearray):
        """Handle bt data."""

        # Ignore notifications we don't expect
        if not self.notify_future or self.notify_future.done():
            _LOGGER.warning("Unexpected notification")
            return

        # If something went wrong, we might get weird data.
        if data == b"AT+NAME?\r" or data == b"AT+ADV?\r":
            err = BadConnectionError("Got AT+ notification")
            self.notify_future.set_exception(err)
            return

        # Save data
        self.notify_response.extend(data)

        if len(self.notify_response) == self.current_command.response_size():
            if self.current_command.is_valid_response(self.notify_response):
                self.notify_future.set_result(self.notify_response)
            else:
                self.notify_future.set_exception(ParseError("Failed checksum"))
        elif self.current_command.is_exception_response(self.notify_response):
            # We got a MODBUS command exception
            msg = f"MODBUS Exception {self.current_command}: {self.notify_response[2]}"
            self.notify_future.set_exception(ModbusError(msg))
