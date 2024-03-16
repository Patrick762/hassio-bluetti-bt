"""Exceptions."""

# Modified copy of https://github.com/warhammerkid/bluetti_mqtt/blob/main/bluetti_mqtt/bluetooth/exc.py


class ParseError(Exception):
    pass


class ModbusError(Exception):
    pass


class BadConnectionError(Exception):
    pass
