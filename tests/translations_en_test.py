import json
from typing import List
import unittest

from bluetti_bt_lib.base_devices import BluettiDevice
from bluetti_bt_lib.devices import DEVICES


class TestTranslationsEn(unittest.TestCase):
    def setUp(self):
        with open("./custom_components/bluetti_bt/translations/en.json") as f:
            self.t = json.load(f)

        devices: List[BluettiDevice] = []

        for Device in DEVICES.values():
            device = Device()

            self.assertIsInstance(device, BluettiDevice)

            if not isinstance(device, BluettiDevice):
                continue

            devices.append(device)

        self.sensor_names = set()
        for device in devices:
            for field in device.get_sensor_fields():
                self.sensor_names.add(field.name)

        self.binary_sensor_names = set()
        for device in devices:
            for field in device.get_bool_fields():
                self.binary_sensor_names.add(field.name)

        self.select_names = set()
        for device in devices:
            for field in device.get_select_fields():
                self.select_names.add(field.name)

        self.switch_names = set()
        for device in devices:
            for field in device.get_switch_fields():
                self.switch_names.add(field.name)

    def test_sensor_translations(self):
        sensor_keys = sorted(self.t["entity"]["sensor"].keys())

        self.assertGreaterEqual(len(sensor_keys), len(self.sensor_names))

        for sensor_name in self.sensor_names:
            self.assertIn(
                sensor_name,
                sensor_keys,
                f"Missing translation for sensor: {sensor_name}",
            )

    def test_binary_sensor_translations(self):
        binary_sensor_keys = sorted(self.t["entity"]["binary_sensor"].keys())

        self.assertGreaterEqual(len(binary_sensor_keys), len(self.binary_sensor_names))

        for sensor_name in self.binary_sensor_names:
            self.assertIn(
                sensor_name,
                binary_sensor_keys,
                f"Missing translation for binary sensor: {sensor_name}",
            )

    def test_select_translations(self):
        select_keys = sorted(self.t["entity"]["select"].keys())

        self.assertGreaterEqual(len(select_keys), len(self.select_names))

        for select_name in self.select_names:
            self.assertIn(
                select_name,
                select_keys,
                f"Missing translation for select: {select_name}",
            )

    def test_switch_translations(self):
        switch_keys = sorted(self.t["entity"]["switch"].keys())

        self.assertGreaterEqual(len(switch_keys), len(self.switch_names))

        for switch_name in self.switch_names:
            self.assertIn(
                switch_name,
                switch_keys,
                f"Missing translation for switch: {switch_name}",
            )
