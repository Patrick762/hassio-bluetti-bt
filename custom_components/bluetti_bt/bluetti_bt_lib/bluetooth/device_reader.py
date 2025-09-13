"""Device reader."""

import asyncio
import logging
from typing import Any, Callable, List, Union, cast
import async_timeout
from bleak import BleakClient, BleakError, BleakScanner
from bleak_retry_connector import establish_connection, BleakClientWithServiceCache

from ..base_devices.BluettiDevice import BluettiDevice
from ..const import NOTIFY_UUID, RESPONSE_TIMEOUT, WRITE_UUID
from ..exceptions import BadConnectionError, ModbusError, ParseError
from ..utils.commands import ReadHoldingRegisters, WriteSingleRegister

_LOGGER = logging.getLogger(__name__)


class DeviceReader:
    def __init__(
        self,
        bleak_client: BleakClient,
        bluetti_device: BluettiDevice,
        future_builder_method: Callable[[], asyncio.Future[Any]],
        persistent_conn: bool = False,
        polling_timeout: int = 45,
        max_retries: int = 5,
        device_address: str | None = None,
    ble_device = None,
    encrypted: bool = False,
    ) -> None:
        self.client = bleak_client
        self.bluetti_device = bluetti_device
        self.create_future = future_builder_method
        self.persistent_conn = persistent_conn
        self.polling_timeout = polling_timeout
        self.max_retries = max_retries
        
        # Store device info for reconnection / encryption
        self.device_address = device_address
        self.ble_device = ble_device
        self.encrypted = encrypted

        if self.encrypted:
            try:
                from .encryption import BluettiEncryption, Message, MessageType  # type: ignore
                self._encryption_cls = BluettiEncryption
                self._Message = Message
                self._MessageType = MessageType
                self.encryption = BluettiEncryption()
            except Exception as e:  # pragma: no cover
                _LOGGER.error("Failed to initialize encryption support: %s", e)
                self.encrypted = False
                self.encryption = None
        else:
            self.encryption = None
        
        # Try to get address from client if not provided
        if not self.device_address:
            try:
                self.device_address = bleak_client.address if hasattr(bleak_client, '_backend') and bleak_client._backend else None
            except (AttributeError, TypeError):
                self.device_address = None

        self.has_notifier = False
        self.notify_future: asyncio.Future[Any] | None = None
        self.current_command = None
        self.notify_response = bytearray()

        # polling mutex to guard against switches
        self.polling_lock = asyncio.Lock()

    async def read_data(
        self, filter_registers: List[ReadHoldingRegisters] | None = None
    ) -> dict | None:
        _LOGGER.info("Reading data")

        if self.bluetti_device is None:
            _LOGGER.error("Device is None")
            return None

        polling_commands = self.bluetti_device.polling_commands
        pack_commands = self.bluetti_device.pack_polling_commands
        if filter_registers is not None:
            polling_commands = filter_registers
            pack_commands = []
        _LOGGER.info("Polling commands: " + ",".join([f"{c.starting_address}-{c.starting_address + c.quantity - 1}" for c in polling_commands]))
        _LOGGER.info("Pack comands: " + ",".join([f"{c.starting_address}-{c.starting_address + c.quantity - 1}" for c in pack_commands]))

        parsed_data: dict = {}

        async with self.polling_lock:
            try:
                async with async_timeout.timeout(self.polling_timeout):
                    # Reconnect if not connected
                    if not self.client.is_connected:
                        # Resolve a BLEDevice object for reconnection
                        ble_device_obj = self.ble_device

                        # Try to get the device object from the client if not provided
                        if ble_device_obj is None and hasattr(self.client, "device"):
                            try:
                                ble_device_obj = getattr(self.client, "device")
                            except Exception:  # best effort
                                ble_device_obj = None

                        # As a last resort, try to find the device by address
                        if ble_device_obj is None and self.device_address:
                            try:
                                ble_device_obj = await BleakScanner.find_device_by_address(self.device_address)
                            except Exception as e:
                                _LOGGER.debug("BleakScanner failed to resolve device by address %s: %s", self.device_address, e)

                        if ble_device_obj is None:
                            _LOGGER.error("No BLEDevice available for reconnection (address=%s)", self.device_address)
                            raise BadConnectionError("No BLEDevice available for reconnection")

                        # Create new client with retry connector using device object
                        self.client = await establish_connection(
                            BleakClientWithServiceCache,
                            ble_device_obj,
                            "DeviceReader",
                        )
                        # Force notifier to be re-attached on the new client
                        self.has_notifier = False

                    # Attach notifier if needed
                    if not self.has_notifier:
                        _LOGGER.debug("Starting notify on %s", NOTIFY_UUID)
                        await self.client.start_notify(
                            NOTIFY_UUID, self._notification_handler
                        )
                        self.has_notifier = True

                    # Wait for encryption handshake to complete if needed
                    if self.encrypted and self.encryption is not None:
                        # Handshake completes asynchronously via notifications
                        # Give it some time (non-blocking small sleeps)
                        wait_attempts = 0
                        max_attempts = 80  # 80 * 0.25s = 20s
                        while not self.encryption.is_ready_for_commands and wait_attempts < max_attempts:
                            await asyncio.sleep(0.25)
                            wait_attempts += 1
                        if not self.encryption.is_ready_for_commands:
                            _LOGGER.warning(
                                "Encryption handshake incomplete after %.2fs (attempts=%d). Aborting polling cycle.",
                                0.25 * max_attempts,
                                wait_attempts,
                            )
                            return None

                    # Pre-compute estimated minimum time (rough heuristic)
                    estimated_min = len(polling_commands) * (RESPONSE_TIMEOUT + 0.1)
                    if estimated_min > self.polling_timeout:
                        _LOGGER.debug(
                            "Configured polling_timeout=%ss likely too low for ~%d commands (est>=%.1fs)",
                            self.polling_timeout,
                            len(polling_commands),
                            estimated_min,
                        )

                    start_monotonic = asyncio.get_event_loop().time()

                    # Execute polling commands with remaining time budget check
                    for command in polling_commands:
                        remaining = self.polling_timeout - (asyncio.get_event_loop().time() - start_monotonic)
                        if remaining <= RESPONSE_TIMEOUT:
                            _LOGGER.debug(
                                "Breaking polling loop early; remaining %.1fs < RESPONSE_TIMEOUT %.1fs",
                                remaining,
                                RESPONSE_TIMEOUT,
                            )
                            break
                        try:
                            body = command.parse_response(
                                await self._async_send_command(command)
                            )
                            _LOGGER.debug("Raw data: %s", body)
                            parsed = self.bluetti_device.parse(
                                command.starting_address, body
                            )
                            _LOGGER.debug("Parsed data: %s", parsed)
                            parsed_data.update(parsed)
                        except ParseError:
                            _LOGGER.warning("Got a parse exception")

                    # Execute pack polling commands
                    if len(pack_commands) > 0 and len(self.bluetti_device.pack_num_field) == 1:
                        _LOGGER.debug("Polling battery packs")
                        for pack in range(1, self.bluetti_device.pack_num_max + 1):
                            _LOGGER.debug("Setting pack_num to %i", pack)

                            # Set current pack number
                            command = self.bluetti_device.build_setter_command(
                                "pack_num", pack
                            )
                            body = command.parse_response(
                                await self._async_send_command(command)
                            )
                            _LOGGER.debug("Raw data set: %s", body)

                            # Check set pack_num
                            set_pack = int.from_bytes(body, byteorder='big')
                            if set_pack != pack:
                                _LOGGER.warning("Pack polling failed (pack_num %i doesn't match expected %i)", set_pack, pack)
                                continue

                            if self.bluetti_device.pack_num_max > 1:
                                # We need to wait after switching packs 
                                # for the data to be available
                                await asyncio.sleep(5)
                            
                            for command in pack_commands:
                                # Request & parse result for each pack
                                try:
                                    body = command.parse_response(
                                        await self._async_send_command(command)
                                    )
                                    parsed = self.bluetti_device.parse(
                                        command.starting_address, body
                                    )
                                    _LOGGER.debug("Parsed data: %s", parsed)

                                    for key, value in parsed.items():
                                        # Ignore likely unavailable pack data
                                        if value != 0:
                                            parsed_data.update({key + str(pack): value})

                                except ParseError:
                                    _LOGGER.warning("Got a parse exception...")

            except TimeoutError as err:
                _LOGGER.error(f"Polling timed out ({self.polling_timeout}s). Trying again later", exc_info=err)
                if self.notify_future and not self.notify_future.done():
                    self.notify_future.cancel()
                return None
            except BleakError as err:
                _LOGGER.error("Bleak error: %s", err)
                return None
            finally:
                # Disconnect if connection not persistant
                if not self.persistent_conn:
                    if self.has_notifier:
                        try:
                            await self.client.stop_notify(NOTIFY_UUID)
                        except Exception:
                            # Ignore errors here
                            pass
                        self.has_notifier = False
                    await self.client.disconnect()

            # Check if dict is empty
            if not parsed_data:
                return None

            # Reset encryption keys after each full polling cycle when not persistent (align upstream)
            if self.encrypted and self.encryption is not None and not self.persistent_conn:
                try:
                    self.encryption.reset()
                except Exception:
                    pass

            return parsed_data

    async def _async_send_command(self, command: Union[ReadHoldingRegisters, WriteSingleRegister]) -> bytes:
        """Send command and return response"""
        try:
            # Prepare to make request
            self.current_command = command
            self.notify_future = self.create_future()
            self.notify_response = bytearray()

            # Make request
            _LOGGER.debug("Requesting %s", command)
            await self.client.write_gatt_char(WRITE_UUID, bytes(command))

            # Wait for response
            res = await asyncio.wait_for(self.notify_future, timeout=RESPONSE_TIMEOUT)

            # Process data
            _LOGGER.debug("Got %s bytes", len(res))
            return cast(bytes, res)

        except TimeoutError:
            _LOGGER.debug("Polling single command timed out (timeout=%ss) for %s", RESPONSE_TIMEOUT, command)
        except asyncio.CancelledError:
            _LOGGER.debug("notify_future cancelled while waiting for %s (treating as empty response)", command)
            return bytes()
        except ModbusError as err:
            _LOGGER.debug(
                "Got an invalid request error for %s: %s",
                command,
                err,
            )
        except (BadConnectionError, BleakError) as err:
            _LOGGER.debug("BLE error while sending %s: %s", command, err)

        # caught an exception, return empty bytes object
        _LOGGER.debug("Returning empty response for %s", command)
        return bytes()

    def _notification_handler(self, _sender: int, data: bytearray):
        """Handle bt data."""

        # Handle encryption wrapping
        if self.encrypted and self.encryption is not None:
            try:
                Message = self._Message  # aliases
                MessageType = self._MessageType
                msg_obj = Message(data)

                if msg_obj.is_pre_key_exchange:
                    # Pre key-exchange messages pass through special states
                    msg_obj.verify_checksum()
                    if msg_obj.type == MessageType.CHALLENGE:
                        challenge_response = self.encryption.msg_challenge(msg_obj)
                        if challenge_response:
                            asyncio.create_task(self.client.write_gatt_char(WRITE_UUID, challenge_response))
                        return
                    if msg_obj.type == MessageType.CHALLENGE_ACCEPTED:
                        _LOGGER.debug("Challenge accepted")
                        return

                # Determine which key/iv we should use
                if self.encryption.unsecure_aes_key is None and not msg_obj.is_pre_key_exchange:
                    _LOGGER.error("Encrypted payload received before key initialization")
                    return

                key, iv = self.encryption.getKeyIv()
                decrypted = Message(self.encryption.aes_decrypt(msg_obj.buffer, key, iv))

                if decrypted.is_pre_key_exchange:
                    decrypted.verify_checksum()
                    if decrypted.type == MessageType.PEER_PUBKEY:
                        peer_pubkey_response = self.encryption.msg_peer_pubkey(decrypted)
                        if peer_pubkey_response:
                            asyncio.create_task(self.client.write_gatt_char(WRITE_UUID, peer_pubkey_response))
                        return
                    if decrypted.type == MessageType.PUBKEY_ACCEPTED:
                        self.encryption.msg_key_accepted(decrypted)
                        return

                # Replace data with decrypted buffer for normal processing
                data = decrypted.buffer
            except Exception as e:  # pragma: no cover
                _LOGGER.debug("Encryption handling error: %s", e)
                return

        # Ignore notifications we don't expect
        if self.notify_future is None or self.notify_future.done():
            _LOGGER.warning("Unexpected notification")
            return

        # If something went wrong, we might get weird data.
        if data == b"AT+NAME?\r" or data == b"AT+ADV?\r":
            err = BadConnectionError("Got AT+ notification")
            self.notify_future.set_exception(err)
            return

        # Save data
        self.notify_response.extend(data)
    
        # Check if current_command is None before accessing its methods
        if self.current_command is None:
            _LOGGER.warning("Received notification but current_command is None")
            self.notify_future.set_exception(BadConnectionError("No current command"))
            return
    
        if len(self.notify_response) == self.current_command.response_size():
            if self.current_command.is_valid_response(self.notify_response):
                self.notify_future.set_result(self.notify_response)
            else:
                _LOGGER.debug("CRC failed for %s: %s", self.current_command, self.notify_response.hex())
                self.notify_future.set_exception(ParseError("Failed checksum"))
        elif self.current_command.is_exception_response(self.notify_response):
            # We got a MODBUS command exception
            msg = f"MODBUS Exception {self.current_command}: {self.notify_response[2]}"
            self.notify_future.set_exception(ModbusError(msg))
