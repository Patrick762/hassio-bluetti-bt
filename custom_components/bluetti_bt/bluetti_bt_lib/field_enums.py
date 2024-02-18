"""Enums for fields."""

from enum import Enum, unique


@unique
class OutputMode(Enum):
    STOP = 0
    INVERTER_OUTPUT = 1
    BYPASS_OUTPUT_C = 2
    BYPASS_OUTPUT_D = 3
    LOAD_MATCHING = 4


@unique
class AutoSleepMode(Enum):
    THIRTY_SECONDS = 2
    ONE_MINUTE = 3
    FIVE_MINUTES = 4
    NEVER = 5


@unique
class UpsMode(Enum):
    CUSTOMIZED = 1
    PV_PRIORITY = 2
    STANDARD = 3
    TIME_CONTROL = 4


@unique
class SplitPhaseMachineType(Enum):
    SLAVE = 0
    MASTER = 1


@unique
class LedMode(Enum):
    LOW = 1
    HIGH = 2
    SOS = 3
    OFF = 4


@unique
class EcoShutdown(Enum):
    ONE_HOUR = 1
    TWO_HOURS = 2
    THREE_HOURS = 3
    FOUR_HOURS = 4


@unique
class ChargingMode(Enum):
    STANDARD = 0
    SILENT = 1
    TURBO = 2
