import json
from typing import List
import unittest

from bluetti_bt_lib.devices import DEVICES


class TestBTNames(unittest.TestCase):
    def setUp(self):
        with open("./custom_components/bluetti_bt/manifest.json") as f:
            self.manifest = json.load(f)

        self.device_names: List[str] = []
        for name in DEVICES.keys():
            self.device_names.append(name)

    def test_bt_matcher_length(self):
        bt_matcher = self.manifest["bluetooth"]
        for entry in bt_matcher:
            local_name = entry["local_name"]
            self.assertIsInstance(local_name, str)

            if not isinstance(local_name, str):
                continue

            self.assertGreaterEqual(len(local_name.strip("*")), 3)

    def test_device_names(self):
        matchers: List[str] = []

        bt_matcher = self.manifest["bluetooth"]
        for entry in bt_matcher:
            local_name = entry["local_name"]
            if not isinstance(local_name, str):
                continue
            matchers.append(local_name)

        for name in self.device_names:
            found = filter(lambda m: m.endswith("*") and name.startswith(m.strip("*")), matchers)
            self.assertGreaterEqual(len(list(found)), 1, f"Missing BT matcher for device: {name}")
