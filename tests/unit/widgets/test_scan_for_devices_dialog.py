import unittest

import pytest
from bleak.backends.device import BLEDevice

from blueheeler.models.adapters.bledeviceadapter import BleDeviceAdapter
from blueheeler.widgets.scan_for_devices_dialog import DeviceListViewFactory, DeviceRowWidget
from tests.mocks.mock_list_item import MockListItem


@pytest.mark.asyncio
class TestMessageColumnFactory(unittest.TestCase):
    def test_device_row_widget(self):
        """Verify that DeviceListViewFactory correctly binds BleDeviceAdapter to DeviceRowWidget."""
        factory = DeviceListViewFactory()
        device_adapter = BleDeviceAdapter(BLEDevice(name="test_name", address="test_address", details=None))
        list_item = MockListItem(device_adapter)
        factory.emit("setup", list_item)
        row_widget = list_item.get_child()
        # Cannot use assertIsInstance, because ruff does not recognize it as a correct types later
        if not isinstance(row_widget, DeviceRowWidget):
            self.fail("Factory should create a DeviceRowWidget")
        factory.emit("bind", list_item)
        self.assertEqual(row_widget.label_address.get_text(), "test_address")
        self.assertEqual(row_widget.label_name.get_text(), "test_name")

    def test_device_row_widget_doubleclick(self):
        """Verify that doubleclick on list item emits correct signals with correct data."""
        selected_device_adapter = None
        def device_selected_handler(factory, device_adapter):
            nonlocal selected_device_adapter 
            selected_device_adapter = device_adapter
        factory = DeviceListViewFactory()
        factory.connect("signal_device_selected", device_selected_handler)
        device_adapter = BleDeviceAdapter(BLEDevice(name="test_name", address="test_address", details=None))
        list_item = MockListItem(device_adapter)
        factory.emit("setup", list_item)
        row_widget = list_item.get_child()
        # Cannot use assertIsInstance, because ruff does not recognize it as a correct types later
        if not isinstance(row_widget, DeviceRowWidget):
            self.fail("Factory should create a DeviceRowWidget")
        factory.emit("bind", list_item)
        row_widget.gesture.emit("released", 2, 0, 0)

        self.assertEqual(selected_device_adapter, device_adapter)


if __name__ == "__main__":
    unittest.main()
