"""Unittest for device builder."""

import unittest

from custom_components.bluetti_bt.bluetti_bt_lib.utils.device_builder import build_device
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac2a import AC2A
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac60 import AC60
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac60p import AC60P
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac70 import AC70
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac70p import AC70P
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac180 import AC180
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac180p import AC180P
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac200l import AC200L
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac200m import AC200M
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac200pl import AC200PL
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac300 import AC300
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac500 import AC500
from custom_components.bluetti_bt.bluetti_bt_lib.devices.eb3a import EB3A
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ep500 import EP500
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ep500p import EP500P
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ep600 import EP600
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ep760 import EP760
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ep800 import EP800


class TestDeviceBuilder(unittest.TestCase):
    def test_build_Unknow(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "PBOX56786746478"
        with self.assertRaises(TypeError):
            build_device(bt_addr, bt_name)

    def _test_device_build(self, bt_name, cls):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, cls)
        self.assertEqual(built.address, bt_addr)

    def test_build_ac2a(self):
        self._test_device_build("AC2A56786746478", AC2A)

    def test_build_ac60(self):
        self._test_device_build("AC6056786746478", AC60)

    def test_build_ac60p(self):
        self._test_device_build("AC60P56786746478", AC60P)

    def test_build_ac70(self):
        self._test_device_build("AC7056786746478", AC70)

    def test_build_ac70p(self):
        self._test_device_build("AC70P56786746478", AC70P)

    def test_build_ac180(self):
        self._test_device_build("AC18056786746478", AC180)

    def test_build_ac180p(self):
        self._test_device_build("AC180P56786746478", AC180P)

    def test_build_ac200l(self):
        self._test_device_build("AC200L56786746478", AC200L)

    def test_build_ac200m(self):
        self._test_device_build("AC200M56786746478", AC200M)

    def test_build_ac200pl(self):
        self._test_device_build("AC200PL56786746478", AC200PL)

    def test_build_ac300(self):
        self._test_device_build("AC30056786746478", AC300)

    def test_build_ac500(self):
        self._test_device_build("AC50056786746478", AC500)

    def test_build_eb3a(self):
        self._test_device_build("EB3A56786746478", EB3A)

    def test_build_ep500(self):
        self._test_device_build("EP50056786746478", EP500)

    def test_build_ep500p(self):
        self._test_device_build("EP500P56786746478", EP500P)

    def test_build_EP600(self):
        self._test_device_build("EP60056786746478", EP600)

    def test_build_EP760(self):
        self._test_device_build("EP76056786746478", EP760)

    def test_build_EP800(self):
        self._test_device_build("EP80056786746478", EP800)

if __name__ == '__main__':
    unittest.main()
