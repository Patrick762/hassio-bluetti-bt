"""Struct definitions."""

# Copy of https://github.com/warhammerkid/bluetti_mqtt/blob/main/bluetti_mqtt/core/devices/struct.py

from decimal import Decimal
from enum import Enum
from .commands import ReadHoldingRegisters
import struct
from typing import Any, List, Optional, Tuple, Type


def swap_bytes(data: bytes):
    """Swaps the place of every other byte, returning a new byte array"""
    arr = bytearray(data)
    for i in range(0, len(arr) - 1, 2):
        arr[i], arr[i + 1] = arr[i + 1], arr[i]
    return arr


class DeviceField:
    def __init__(self, name: str, address: int, size: int):
        self.name = name
        self.address = address
        self.size = size

    def parse(self, data: bytes) -> Any:
        raise NotImplementedError

    def in_range(self, val: Any) -> bool:
        return True


class UintField(DeviceField):
    def __init__(self, name: str, address: int, range: Optional[Tuple[int, int]], multiplier: float):
        self.range = range
        self.multiplier = multiplier
        super().__init__(name, address, 1)

    def parse(self, data: bytes) -> int:
        val = struct.unpack("!H", data)[0]

        return val * self.multiplier

    def in_range(self, val: int) -> bool:
        if self.range is None:
            return True
        else:
            return val >= self.range[0] and val <= self.range[1]


class IntField(DeviceField):
    def __init__(self, name: str, address: int, range: Optional[Tuple[int, int]]):
        self.range = range
        super().__init__(name, address, 1)

    def parse(self, data: bytes) -> int:
        return struct.unpack(">h", data)[0]

    def in_range(self, val: int) -> bool:
        if self.range is None:
            return True
        else:
            return val >= self.range[0] and val <= self.range[1]


class BoolField(DeviceField):
    def __init__(self, name: str, address: int):
        super().__init__(name, address, 1)

    def parse(self, data: bytes) -> bool:
        return struct.unpack("!H", data)[0] == 1


class EnumField(DeviceField):
    def __init__(self, name: str, address: int, enum: Type[Enum]):
        self.enum = enum
        super().__init__(name, address, 1)

    def parse(self, data: bytes) -> Any:
        val = struct.unpack("!H", data)[0]
        return self.enum(val)


class DecimalField(DeviceField):
    def __init__(
        self, name: str, address: int, scale: int, range: Optional[Tuple[int, int]], multiplier: float
    ):
        self.scale = scale
        self.range = range
        self.multiplier = multiplier
        super().__init__(name, address, 1)

    def parse(self, data: bytes) -> Decimal:
        val = Decimal(struct.unpack("!H", data)[0])
        return (val / 10 ** self.scale) * Decimal(self.multiplier)

    def in_range(self, val: Decimal) -> bool:
        if self.range is None:
            return True
        else:
            return val >= self.range[0] and val <= self.range[1]


class DecimalArrayField(DeviceField):
    def __init__(self, name: str, address: int, size: int, scale: int):
        self.scale = scale
        super().__init__(name, address, size)

    def parse(self, data: bytes) -> Decimal:
        values = list(struct.unpack(f"!{self.size}H", data))
        return [Decimal(v) / 10 ** self.scale for v in values]


class StringField(DeviceField):
    """Fixed-width null-terminated string field"""

    def parse(self, data: bytes) -> str:
        return data.rstrip(b"\0").decode("ascii")


class SwapStringField(DeviceField):
    """Fixed-width null-terminated string field"""

    def parse(self, data: bytes) -> str:
        return swap_bytes(data).rstrip(b"\0").decode("ascii")


class VersionField(DeviceField):
    def __init__(self, name: str, address: int):
        super().__init__(name, address, 2)

    def parse(self, data: bytes) -> int:
        values = struct.unpack("!2H", data)
        return Decimal(values[0] + (values[1] << 16)) / 100


class SerialNumberField(DeviceField):
    def __init__(self, name: str, address: int):
        super().__init__(name, address, 4)

    def parse(self, data: bytes) -> int:
        values = struct.unpack("!4H", data)
        return values[0] + (values[1] << 16) + (values[2] << 32) + (values[3] << 48)


class DeviceStruct:
    fields: List[DeviceField]

    def __init__(self):
        self.fields = []

    def add_uint_field(self, name: str, address: int, range: Tuple[int, int] = None, multiplier: float = 1):
        self.fields.append(UintField(name, address, range, multiplier))

    def add_int_field(self, name: str, address: int, range: Tuple[int, int] = None):
        self.fields.append(IntField(name, address, range))

    def add_bool_field(self, name: str, address: int):
        self.fields.append(BoolField(name, address))

    def add_enum_field(self, name: str, address: int, enum: Type[Enum]):
        self.fields.append(EnumField(name, address, enum))

    def add_decimal_field(
        self, name: str, address: int, scale: int, range: Tuple[int, int] = None, multiplier: float = 1
    ):
        self.fields.append(DecimalField(name, address, scale, range, multiplier))

    def add_decimal_array_field(self, name: str, address: int, size: int, scale: int):
        self.fields.append(DecimalArrayField(name, address, size, scale))

    def add_string_field(self, name: str, address: int, size: int):
        self.fields.append(StringField(name, address, size))

    def add_swap_string_field(self, name: str, address: int, size: int):
        self.fields.append(SwapStringField(name, address, size))

    def add_version_field(self, name: str, address: int):
        self.fields.append(VersionField(name, address))

    def add_sn_field(self, name: str, address: int):
        self.fields.append(SerialNumberField(name, address))
        
    def get_read_holding_registers(self, tolerance=20, filter=lambda address: True):
        address_set = set()
        for field in self.fields:
            for address in range(field.address, field.address + field.size):
                address_set.add(address)
        # Filter out addresses that we specificly 
        # specified to exclude.
        for address in set(address_set):
            if not filter(address):
                address_set.remove(address)
        # Fast path: no addresses -> no commands.
        if not address_set:
            return []
        
        commands = []

        address_list = sorted(address_set)
        start = address_list[0]
        last = address_list[0]
        for address in address_list[1:]:
            # Create a new group if there's a gap 
            # in the addresses.
            if address >= last + tolerance:
                commands.append(ReadHoldingRegisters(start, last - start + 1))
                start = address
            last = address
        commands.append(ReadHoldingRegisters(start, last - start + 1))    
        return commands

    def parse(self, starting_address: int, data: bytes) -> dict:
        # Offsets and size are counted in 2 byte chunks, so for the range we
        # need to divide the byte size by 2
        data_size = int(len(data) / 2)

        # Filter out fields not in range
        r = range(starting_address, starting_address + data_size)
        fields = [
            f for f in self.fields if f.address in r and f.address + f.size - 1 in r
        ]

        # Parse fields
        parsed = {}
        for f in fields:
            data_start = 2 * (f.address - starting_address)
            field_data = data[data_start : data_start + 2 * f.size]
            val = f.parse(field_data)

            # Skip if the value is "out-of-range" - sometimes the sensors
            # report weird values
            if not f.in_range(val):
                continue

            parsed[f.name] = val

        return parsed
