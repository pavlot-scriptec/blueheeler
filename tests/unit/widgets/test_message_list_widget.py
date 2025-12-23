import gi

gi.require_version("Gtk", "4.0")
import unittest

import pytest
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.descriptor import BleakGATTDescriptor
from bleak.backends.device import BLEDevice
from bleak.backends.service import BleakGATTService
from faker import Faker
from gi.repository import Gtk

from blueheeler.models.adapters.blecharacteristicadapter import BleCharacteristicAdapter
from blueheeler.models.adapters.blecharacteristicdescriptoradapter import (
    BleCharacteristicDescriptorAdapter,
)
from blueheeler.models.adapters.bledeviceadapter import BleDeviceAdapter
from blueheeler.models.adapters.bleserviceadapter import BleServiceAdapter
from blueheeler.models.data_packet import DataPacket
from blueheeler.widgets.message_list_widget import MessageColumnFactory
from tests.mocks.mock_list_item import MockListItem

faker = Faker()


class TestMessageColumnFactory:

    def __test_labels_data(): # type: ignore[misc]
        result = []
        for service in [
            BleServiceAdapter(
                device=BleDeviceAdapter(
                    device=BLEDevice(
                        address="fake_address", name="fake_name", details=None
                    )
                ),
                service=BleakGATTService(obj=None, handle=1, uuid=faker.uuid4()),
            ),
        ]:
            expected_device_addr = ""
            expected_device_name = ""
            expected_service_uuid = ""
            expected_service_description = ""

            for characteristic in [
                BleCharacteristicAdapter(
                    service=service,
                    characteristic=BleakGATTCharacteristic(
                        obj=None,
                        handle=1,
                        uuid=faker.uuid4(),
                        properties=[],
                        max_write_without_response_size=lambda: 0,
                        service=service.service,
                    ),
                ),
            ]:
                for descriptor in [
                    None,
                    BleCharacteristicDescriptorAdapter(
                        characteristic=characteristic,
                        descriptor=BleakGATTDescriptor(
                            obj=None,
                            handle=1,
                            uuid=faker.uuid4(),
                            characteristic=characteristic.characteristic,
                        ),
                    ),
                ]:
                    expected_characteristic_description = (
                        "Unknown"
                        if characteristic.description is None
                        else characteristic.description
                    )
                    expected_characteristic_uuid = characteristic.uuid

                    expected_device_addr = service.device.address
                    expected_device_name = service.device.name
                    expected_service_uuid = service.uuid
                    expected_service_description = service.description

                    expected_descriptor_description = ""
                    expected_descriptor_uuid = ""
                    if descriptor:
                        expected_descriptor_description = descriptor.description
                        expected_descriptor_uuid = descriptor.uuid

                    for is_incoming in [True, False]:
                        for data in [b"xxxxx", b"x", b""]:
                            message: DataPacket = DataPacket(
                                characteristic=characteristic,
                                descriptor=descriptor,
                                data=data,
                                is_incoming=is_incoming,
                            )
                            result.append(
                                (
                                    message,
                                    {
                                        "timestamp": message.timestamp.format_iso8601(),
                                        "characteristic.service.device.address": expected_device_addr,
                                        "characteristic.service.device.name": expected_device_name,
                                        "characteristic.service.uuid": expected_service_uuid,
                                        "characteristic.service.description": expected_service_description,
                                        "characteristic.description": expected_characteristic_description,
                                        "characteristic.uuid": expected_characteristic_uuid,
                                        "descriptor.description": expected_descriptor_description,
                                        "descriptor.uuid": expected_descriptor_uuid,
                                        "size": str(len(data)),
                                        "is_incoming": str(is_incoming),
                                    },
                                )
                            )

        return result

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ["data_message", "expected_path_values"], __test_labels_data()
    )
    async def test_labels(self, data_message, expected_path_values):
        """Verify that MessageColumnFactory correctly binds DataMessage to label text."""
        list_item = MockListItem(data_message)
        for path, value in expected_path_values.items():
            self.__check_label(list_item=list_item, path=path, expected=value)

    def __check_label(self, list_item, path, expected):
        factory = MessageColumnFactory(path)
        factory.emit("setup", list_item)
        label = list_item.get_child()
        assert isinstance(label, Gtk.Label), "Factory should create a Gtk.Label"
        factory.emit("bind", list_item)
        actual = label.get_text()
        assert actual == expected, f"Path: {path}, expected {expected}, actual {actual}"


if __name__ == "__main__":
    unittest.main()
