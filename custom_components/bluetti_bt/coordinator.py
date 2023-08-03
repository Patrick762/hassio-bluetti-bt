"""Coordinator for Bluetti integration."""

from __future__ import annotations
from typing import List

import asyncio
from datetime import timedelta
import logging
from typing import cast
import async_timeout

from bleak import BleakClient, BleakError

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from bluetti_mqtt.bluetooth.client import BluetoothClient
from bluetti_mqtt.bluetooth import (
    BadConnectionError,
    ModbusError,
    ParseError,
    build_device,
)
from bluetti_mqtt.core.devices.bluetti_device import BluettiDevice
from bluetti_mqtt.core.commands import ReadHoldingRegisters

_LOGGER = logging.getLogger(__name__)


class DummyDevice(BluettiDevice):
    """Dummy device used to add more fields to existing devices.

    Changes made here are only temporary and should also be
    contributed to https://github.com/warhammerkid/bluetti_mqtt
    """

    def __init__(self, device: BluettiDevice):
        """Init dummy device with real device."""
        self.struct = device.struct

        if device.type == "EP600":
            self.struct.add_decimal_field("adl400_ac_input_voltage_phase1", 1229, 1)
            self.struct.add_decimal_field("adl400_ac_input_voltage_phase2", 1237, 1)
            self.struct.add_decimal_field("adl400_ac_input_voltage_phase3", 1245, 1)
            self.struct.add_decimal_field("ac_input_voltage_phase1", 1314, 1)
            self.struct.add_decimal_field("ac_input_voltage_phase2", 1320, 1)
            self.struct.add_decimal_field("ac_input_voltage_phase3", 1326, 1)
            self.struct.add_decimal_field("ac_output_voltage_phase1", 1511, 1)
            self.struct.add_decimal_field("ac_output_voltage_phase2", 1518, 1)
            self.struct.add_decimal_field("ac_output_voltage_phase3", 1525, 1)

        super().__init__(device.address, device.type, device.sn)
        self._parent = device

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        if self.type == "EP600":
            return [
                ReadHoldingRegisters(100, 62),
                ReadHoldingRegisters(1229, 19),
                ReadHoldingRegisters(1314, 13),
                ReadHoldingRegisters(1511, 15),
                ReadHoldingRegisters(2022, 6),
                ReadHoldingRegisters(2213, 4),
                # Battery
                ReadHoldingRegisters(6101, 7),
                ReadHoldingRegisters(6175, 11),
            ]

        return self._parent.polling_commands

    @property
    def pack_polling_commands(self) -> List[ReadHoldingRegisters]:
        return self._parent.pack_logging_commands

    @property
    def logging_commands(self) -> List[ReadHoldingRegisters]:
        return self._parent.logging_commands

    @property
    def pack_logging_commands(self) -> List[ReadHoldingRegisters]:
        return self._parent.pack_logging_commands

    @property
    def writable_ranges(self) -> List[range]:
        return self._parent.writable_ranges


class PollingCoordinator(DataUpdateCoordinator):
    """Polling coordinator."""

    def __init__(self, hass: HomeAssistant, address, device_name: str):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Bluetti polling coordinator",
            update_interval=timedelta(seconds=20),
        )
        self._address = address
        self.notify_future = None
        self.current_command = None
        self.notify_response = bytearray()
        bluetti_device = build_device(address, device_name)

        # Add or modify device fields
        self.bluetti_device = DummyDevice(bluetti_device)

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        self.logger.debug("Polling data")

        device = bluetooth.async_ble_device_from_address(self.hass, self._address)
        if device is None:
            self.logger.error("Device %s not available", self._address)
            return None

        if self.bluetti_device is None:
            self.logger.error("Device type for %s not found", self._address)
            return None

        # Polling
        client = BleakClient(device)
        parsed_data: dict = {}

        try:
            async with async_timeout.timeout(15):
                await client.connect()

                await client.start_notify(
                    BluetoothClient.NOTIFY_UUID, self._notification_handler
                )

                for command in self.bluetti_device.polling_commands:
                    try:
                        # Prepare to make request
                        self.current_command = command
                        self.notify_future = self.hass.loop.create_future()
                        self.notify_response = bytearray()

                        # Make request
                        self.logger.debug("Requesting %s", command)
                        await client.write_gatt_char(
                            BluetoothClient.WRITE_UUID, bytes(command)
                        )

                        # Wait for response
                        res = await asyncio.wait_for(
                            self.notify_future, timeout=BluetoothClient.RESPONSE_TIMEOUT
                        )

                        # Process data
                        self.logger.debug("Got %s bytes", len(res))
                        response = cast(bytes, res)
                        body = command.parse_response(response)
                        parsed = self.bluetti_device.parse(
                            command.starting_address, body
                        )

                        self.logger.debug("Parsed data: %s", parsed)
                        parsed_data.update(parsed)

                    except TimeoutError:
                        self.logger.error(
                            "Polling timed out (address: %s)", self._address
                        )
                    except ParseError:
                        self.logger.warning("Got a parse exception...")
                    except ModbusError as err:
                        self.logger.warning(
                            "Got an invalid request error for %s: %s",
                            command,
                            err,
                        )
                    except (BadConnectionError, BleakError) as err:
                        self.logger.warning(
                            "Needed to disconnect due to error: %s", err
                        )
        except TimeoutError:
            self.logger.error("Polling timed out for device %s", self._address)
            return None
        except BleakError as err:
            self.logger.error("Bleak error: %s", err)
            return None
        finally:
            await client.disconnect()

        # Pass data back to sensors
        return parsed_data

    def _notification_handler(self, _sender: int, data: bytearray):
        """Handle bt data."""

        # Ignore notifications we don't expect
        if not self.notify_future or self.notify_future.done():
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
