"""Bluetti device."""

# Reduced copy of https://github.com/warhammerkid/bluetti_mqtt/blob/main/bluetti_mqtt/core/devices/bluetti_device.py

from typing import Any, List

from ..utils.commands import ReadHoldingRegisters, WriteSingleRegister
from ..utils.struct import BoolField, DeviceStruct, EnumField


class BluettiDevice:
    struct: DeviceStruct

    def __init__(self, address: str, type: str, sn: str):
        self.address = address
        self.type = type
        self.sn = sn

    def parse(self, address: int, data: bytes) -> dict:
        return self.struct.parse(address, data)

    @property
    def pack_num_max(self):
        """
        A given device has a maximum number of battery packs, including the
        internal battery if it has one. We can provide this information statically
        so it's not necessary to poll the device.
        """
        return 1

    @property
    def polling_commands(self) -> List[ReadHoldingRegisters]:
        """A given device has an optimal set of commands for polling"""
        raise NotImplementedError

    @property
    def pack_polling_commands(self) -> List[ReadHoldingRegisters]:
        """A given device may have a set of commands for polling pack data"""
        return []

    @property
    def writable_ranges(self) -> List[range]:
        """The address ranges that are writable"""
        return []
    
    @property
    def pack_num_field(self) -> List[ReadHoldingRegisters]:
        """The address 'range' of the pack num result. Matches pack_num_result"""
        return []

    def has_field(self, field: str):
        return any(f.name == field for f in self.struct.fields)

    def has_field_setter(self, field: str):
        matches = [f for f in self.struct.fields if f.name == field]
        return any(any(f.address in r for r in self.writable_ranges) for f in matches)

    def build_setter_command(self, field: str, value: Any):
        matches = [f for f in self.struct.fields if f.name == field]
        device_field = next(
            f for f in matches if any(f.address in r for r in self.writable_ranges)
        )

        # Convert value to an integer
        if isinstance(device_field, EnumField):
            value = device_field.enum[value].value
        elif isinstance(device_field, BoolField):
            value = 1 if value else 0

        return WriteSingleRegister(device_field.address, value)
