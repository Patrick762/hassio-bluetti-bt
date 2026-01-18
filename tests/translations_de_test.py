import json
from typing import List
import unittest

from bluetti_bt_lib.base_devices import BluettiDevice
from bluetti_bt_lib.devices import DEVICES


class TestTranslationsDe(unittest.TestCase):
    def setUp(self):
        with open("./custom_components/bluetti_bt/translations/de.json") as f:
            self.t = json.load(f)

        devices: List[BluettiDevice] = []

        for Device in DEVICES.values():
            device = Device()

            self.assertIsInstance(device, BluettiDevice)

            if not isinstance(device, BluettiDevice):
                continue

            devices.append(device)

        self.sensor_names = set()
        self.binary_sensor_names = set()
        self.select_names = set()
        self.switch_names = set()

        for device in devices:
            for field in device.get_sensor_fields() + device.get_select_fields():
                self.sensor_names.add(field.name)
            for field in device.get_bool_fields() + device.get_switch_fields():
                self.binary_sensor_names.add(field.name)
            for field in device.get_select_fields():
                self.select_names.add(field.name)
            for field in device.get_switch_fields():
                self.switch_names.add(field.name)

    def test_sensor_translations(self):
        sensor_keys = sorted(self.t["entity"]["sensor"].keys())

        for sensor_name in self.sensor_names:
            self.assertIn(
                sensor_name,
                sensor_keys,
                f"Missing translation for sensor: {sensor_name}",
            )

    def test_binary_sensor_translations(self):
        binary_sensor_keys = sorted(self.t["entity"]["binary_sensor"].keys())

        for sensor_name in self.binary_sensor_names:
            self.assertIn(
                sensor_name,
                binary_sensor_keys,
                f"Missing translation for binary sensor: {sensor_name}",
            )

    def test_select_translations(self):
        select_keys = sorted(self.t["entity"]["select"].keys())

        for select_name in self.select_names:
            self.assertIn(
                select_name,
                select_keys,
                f"Missing translation for select: {select_name}",
            )

    def test_switch_translations(self):
        switch_keys = sorted(self.t["entity"]["switch"].keys())

        for switch_name in self.switch_names:
            self.assertIn(
                switch_name,
                switch_keys,
                f"Missing translation for switch: {switch_name}",
            )
