from unittest.mock import MagicMock

import gi
import pytest

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

from automation.widgets.write_dialog_automation import WriteDialogAutomation
from blueheeler.models.adapters.blecharacteristicadapter import BleCharacteristicAdapter
from blueheeler.models.adapters.blecharacteristicdescriptoradapter import (
    BleCharacteristicDescriptorAdapter,
)
from blueheeler.models.adapters.bledevicecontroller import BleDeviceController
from blueheeler.widgets.write_dialog import WriteDialog


@pytest.mark.asyncio
class TestWriteDialog:

    async def test_write_characteristic(self):
        mock_parent = Gtk.Window()
        mock_controller = MagicMock(spec=BleDeviceController)
        mock_characteristic = MagicMock(spec=BleCharacteristicAdapter)

        dialog = WriteDialog(
            parent=mock_parent,
            device_controller=mock_controller,
            write_object=mock_characteristic,
        )

        automation = WriteDialogAutomation(dialog)

        automation.enter_text("ABC")
        automation.click_write()

        mock_controller.write_characteristic.assert_called_once()

        args, _ = mock_controller.write_characteristic.call_args
        written_bytes = args[1]

        assert isinstance(written_bytes, GLib.Bytes)
        assert written_bytes.get_data() == b"ABC"


    async def test_write_descriptor(self):
        mock_parent = Gtk.Window()
        mock_controller = MagicMock(spec=BleDeviceController)
        mock_desc = MagicMock(spec=BleCharacteristicDescriptorAdapter)

        dialog = WriteDialog(
            parent=mock_parent,
            device_controller=mock_controller,
            write_object=mock_desc,
        )

        automation = WriteDialogAutomation(dialog)

        automation.enter_text("123")
        automation.click_write()

        mock_controller.write_descriptor.assert_called_once()

        args, _ = mock_controller.write_descriptor.call_args
        written_bytes = args[1]

        assert written_bytes.get_data() == b"123"
