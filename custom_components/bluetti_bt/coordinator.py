"""Coordinator for Bluetti integration."""

from __future__ import annotations
from typing import List, cast

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

from bluetti_mqtt.bluetooth.client import BluetoothClient
from bluetti_mqtt.bluetooth import (
    BadConnectionError,
    ModbusError,
    ParseError,
    build_device,
)
from bluetti_mqtt.core.devices.bluetti_device import BluettiDevice
from bluetti_mqtt.core.commands import ReadHoldingRegisters

from .const import DATA_POLLING_RUNNING, DOMAIN
from .utils import mac_loggable

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
            # DC Solar Input (copied from PR https://github.com/warhammerkid/bluetti_mqtt/pull/87 by KM011092)
            self.struct.add_uint_field('pv_input_power1', 1212)  # MPP 1 in - value * 0.1
            #self.struct.add_uint_field('pv_input_voltage1', 1213)  # MPP 1 in  - value * 0.1
            #self.struct.add_uint_field('pv_input_current1', 1214)  # MPP 1 in
            self.struct.add_uint_field('pv_input_power2', 1220)  # MPP 2 in  - value * 0.1
            #self.struct.add_uint_field('pv_input_voltage2', 1221)  # MPP 2 in  - value * 0.1
            #self.struct.add_uint_field('pv_input_current2', 1222)  # MPP 2 in
            # ADL400 Smart Meter for AC Solar
            self.struct.add_uint_field("adl400_ac_input_power_phase1", 1228)
            self.struct.add_uint_field("adl400_ac_input_power_phase2", 1236)
            self.struct.add_uint_field("adl400_ac_input_power_phase3", 1244)
            self.struct.add_decimal_field("adl400_ac_input_voltage_phase1", 1229, 1)
            self.struct.add_decimal_field("adl400_ac_input_voltage_phase2", 1237, 1)
            self.struct.add_decimal_field("adl400_ac_input_voltage_phase3", 1245, 1)
            # Grid Input
            self.struct.add_decimal_field("grid_input_frequency", 1300, 1)
            self.struct.add_uint_field("grid_input_power_phase1", 1313)
            self.struct.add_uint_field("grid_input_power_phase2", 1319)
            self.struct.add_uint_field("grid_input_power_phase3", 1325)
            self.struct.add_decimal_field("grid_input_voltage_phase1", 1314, 1)
            self.struct.add_decimal_field("grid_input_voltage_phase2", 1320, 1)
            self.struct.add_decimal_field("grid_input_voltage_phase3", 1326, 1)
            self.struct.add_decimal_field("grid_input_current_phase1", 1315, 1)
            self.struct.add_decimal_field("grid_input_current_phase2", 1321, 1)
            self.struct.add_decimal_field("grid_input_current_phase3", 1327, 1)
            # EP600 AC Output
            self.struct.add_decimal_field("ac_output_frequency", 1500, 1)
            self.struct.add_uint_field("ac_output_power_phase1", 1510)
            self.struct.add_uint_field("ac_output_power_phase2", 1517)
            self.struct.add_uint_field("ac_output_power_phase3", 1524)
            self.struct.add_decimal_field("ac_output_voltage_phase1", 1511, 1)
            self.struct.add_decimal_field("ac_output_voltage_phase2", 1518, 1)
            self.struct.add_decimal_field("ac_output_voltage_phase3", 1525, 1)
            self.struct.add_decimal_field("ac_output_current_phase1", 1512, 1)
            self.struct.add_decimal_field("ac_output_current_phase2", 1519, 1)
            self.struct.add_decimal_field("ac_output_current_phase3", 1526, 1)

        super().__init__(device.address, device.type, device.sn)
        self._parent = device

    @property
    def pack_num_max(self):
        return self._parent.pack_num_max

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        if self.type == "EP600":
            return [
                ReadHoldingRegisters(100, 62),
                ReadHoldingRegisters(1228, 19),
                ReadHoldingRegisters(1300, 28),
                ReadHoldingRegisters(1500, 27),
                ReadHoldingRegisters(2022, 6),
                ReadHoldingRegisters(2213, 4),
                ReadHoldingRegisters(1212, 11),
                # Battery
                ReadHoldingRegisters(6101, 7),
                ReadHoldingRegisters(6175, 11),
            ]

        return self._parent.polling_commands

    @property
    def pack_polling_commands(self) -> List[ReadHoldingRegisters]:
        if self.type == "EP600":
            return []
        return self._parent.pack_polling_commands

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

    def __init__(
        self,
        hass: HomeAssistant,
        address: str,
        device_name: str,
        polling_interval: int,
        persistent_conn: bool,
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
        bluetti_device = build_device(address, device_name)
        self.persistent_conn = persistent_conn

        # Add or modify device fields
        self.bluetti_device = DummyDevice(bluetti_device)

        # Create client
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
                async with async_timeout.timeout(45):

                    # Reconnect if not connected
                    max_retries = 5
                    for attempt in range(1,max_retries + 1):
                        try:
                            if not self.client.is_connected:
                                await self.client.connect()
                            break
                        except Exception as e:
                            if attempt == max_retries:
                                raise  # pass exception on max_retries attempt
                            else:
                                self.logger.debug(f"Connect unsucessful (attempt {attempt}): {e}. Retrying...")
                                await asyncio.sleep(2)

                    # Attach notifier if needed
                    if not self.has_notifier:
                        await self.client.start_notify(
                            BluetoothClient.NOTIFY_UUID, self._notification_handler
                        )
                        self.has_notifier = True

                    for command in self.bluetti_device.polling_commands:
                        try:
                            body = command.parse_response(
                                await self.async_send_command(command)
                            )
                            parsed = self.bluetti_device.parse(
                                command.starting_address, body
                            )
                            self.logger.debug("Parsed data: %s", parsed)
                            parsed_data.update(parsed)

                        except ParseError:
                            self.logger.warning("Got a parse exception...")

                    if len(self.bluetti_device.pack_polling_commands) > 0:
                        _LOGGER.debug("Polling battery packs")
                        # pack polling
                        for pack in range (1, self.bluetti_device.pack_num_max + 1):
                            # Set current pack number
                            await self.async_send_command(
                                self.bluetti_device.build_setter_command('pack_num', pack)
                                )

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
                self.logger.debug("Polling timed out for device %s", mac_loggable(self._address))
                return None
            except BleakError as err:
                self.logger.warning("Bleak error: %s", err)
                return None
            finally:
                # Disconnect if connection not persistant
                if not self.persistent_conn:
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
                BluetoothClient.WRITE_UUID, bytes(command)
            )

            # Wait for response
            res = await asyncio.wait_for(
                self.notify_future, timeout=BluetoothClient.RESPONSE_TIMEOUT
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
