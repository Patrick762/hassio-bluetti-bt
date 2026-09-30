import unittest

from bluetti_bt_lib import build_device
from bluetti_bt_lib.devices import DEVICES

from custom_components.bluetti_bt.utils import sanitize_device_name


class TestDeviceName(unittest.TestCase):
    def test_sanitized_name_builds_device(self):
        # The config flow stores the sanitized name, which is later passed to build_device
        for name, cls in DEVICES.items():
            sanitized = sanitize_device_name(name + "12345678")
            self.assertIsInstance(build_device(sanitized), cls, sanitized)

    def test_invalid_characters_removed(self):
        self.assertEqual(
            sanitize_device_name("AC180\x00123-456 "),
            "AC180123456",
        )
        self.assertEqual(
            sanitize_device_name("Handsfree 2\x0022441000285013"),
            "Handsfree 222441000285013",
        )
