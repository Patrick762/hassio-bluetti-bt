"""Unittest for device builder."""

import unittest

from custom_components.bluetti_bt.bluetti_bt_lib.utils.device_builder import build_device
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac60 import AC60
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac70 import AC70
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac70p import AC70P
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac180 import AC180
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac180p import AC180P
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac200l import AC200L
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac200m import AC200M
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac300 import AC300
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ac500 import AC500
from custom_components.bluetti_bt.bluetti_bt_lib.devices.eb3a import EB3A
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ep500 import EP500
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ep500p import EP500P
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ep600 import EP600
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ep760 import EP760
from custom_components.bluetti_bt.bluetti_bt_lib.devices.ep800 import EP800
from custom_components.bluetti_bt.bluetti_bt_lib.devices.elite100v2 import Elite100V2


class TestDeviceBuilder(unittest.TestCase):
    def test_build_Unknow(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "PBOX56786746478"
        with self.assertRaises(TypeError):
            build_device(bt_addr, bt_name)

    def test_build_ac60(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "AC6056786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, AC60)
        self.assertEqual(built.address, bt_addr)

    def test_build_ac70(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "AC7056786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, AC70)
        self.assertEqual(built.address, bt_addr)

    def test_build_ac70p(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "AC70P56786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, AC70P)
        self.assertEqual(built.address, bt_addr)

    def test_build_ac180(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "AC18056786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, AC180)
        self.assertEqual(built.address, bt_addr)

    def test_build_ac180p(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "AC180P56786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, AC180P)
        self.assertEqual(built.address, bt_addr)

    def test_build_ac200l(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "AC200L56786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, AC200L)
        self.assertEqual(built.address, bt_addr)

    def test_build_ac200m(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "AC200M56786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, AC200M)
        self.assertEqual(built.address, bt_addr)

    def test_build_ac300(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "AC30056786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, AC300)
        self.assertEqual(built.address, bt_addr)

    def test_build_ac500(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "AC50056786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, AC500)
        self.assertEqual(built.address, bt_addr)

    def test_build_eb3a(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "EB3A56786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, EB3A)
        self.assertEqual(built.address, bt_addr)

    def test_build_ep500(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "EP50056786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, EP500)
        self.assertEqual(built.address, bt_addr)

    def test_build_ep500p(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "EP500P56786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, EP500P)
        self.assertEqual(built.address, bt_addr)

    def test_build_EP600(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "EP60056786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, EP600)
        self.assertEqual(built.address, bt_addr)

    def test_build_EP760(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "EP76056786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, EP760)
        self.assertEqual(built.address, bt_addr)

    def test_build_EP800(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "EP80056786746478"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, EP800)
        self.assertEqual(built.address, bt_addr)

    def test_build_Elite100V2(self):
        bt_addr = "aa:bb:cc:dd:ee:ff"
        bt_name = "EL100V20123456789012"
        built = build_device(bt_addr, bt_name)

        self.assertIsInstance(built, Elite100V2)
        self.assertEqual(built.address, bt_addr)

if __name__ == '__main__':
    unittest.main()
