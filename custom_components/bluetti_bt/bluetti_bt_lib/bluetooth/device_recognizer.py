"""Device recognizer."""

import asyncio
import logging
from typing import Any, Callable
from bleak import BleakClient

from custom_components.bluetti_bt.bluetti_bt_lib.utils.commands import (
    ReadHoldingRegisters,
)

from ..base_devices.ProtocolV2Device import ProtocolV2Device
from ..bluetooth.device_reader import DeviceReader

_LOGGER = logging.getLogger(__name__)


async def recognize_device(
    bleak_client: BleakClient,
    future_builder_method: Callable[[], asyncio.Future[Any]],
) -> str:

    # Since we don't know the type we use the base device
    bluetti_device = ProtocolV2Device("Unknown", "Unknown", "Unknown")

    # Create device builder
    device_reader = DeviceReader(bleak_client, bluetti_device, future_builder_method)

    # Retry a few times to get data
    for _ in range(1, 50):
        # We only need 6 registers to get the device type
        data = await device_reader.read_data(
            [
                ReadHoldingRegisters(110, 6),
            ]
        )

        if data is not None:
            break

        await asyncio.sleep(0.1)

    if data is None:
        # Should not happen
        return "Unknown"

    field_data = data.get("device_type")

    if field_data is None:
        # We have a problem
        _LOGGER.error("No data in device type field_datas. Maybe it's a V1 device?")
        return "Unknown"

    if not isinstance(field_data, str):
        # We have a problem
        _LOGGER.error("Invalid data in device type field_datas")
        return "Unknown"

    return field_data
