import gi

gi.require_version("Gtk", "4.0")

from typing import Optional

from bleak.backends.device import BLEDevice
from gi.repository import GObject

from blueheeler.models.adapters.services_collection_adapter import ServicesCollectionAdapter


class BleDeviceAdapter(GObject.Object):
    __gtype_name__ = "BleDeviceAdapter"

    def __init__(self, device: BLEDevice):
        super().__init__()
        self.__device: BLEDevice = device
        self.__services: Optional[ServicesCollectionAdapter] = None

    @GObject.Property(type=str)
    def name(self):
        if self.__device.name is None:
            return ""
        return self.__device.name

    @GObject.Property(type=str)
    def address(self):
        return self.__device.address

    @GObject.Property(type=ServicesCollectionAdapter)
    def services(self):
        return self.__services

    @services.setter # type: ignore[no-redef]
    def services(self, value: ServicesCollectionAdapter): 
        self.__services = value
        self.notify("services")

    def get_device(self):
        return self.__device

    def update(self, device: BLEDevice):
        self.__device = device
        self.notify("name")
        self.notify("address")
        self.notify("services")


class DevicesCollectionAdapter(GObject.Object):
    __gtype_name__ = "DevicesCollectionAdapter"

    def __init__(self, devices: list[BLEDevice]):
        super().__init__()
        self.__devices: list[BleDeviceAdapter] = []
        for device in devices:
            self.__devices.append(BleDeviceAdapter(device))

    def __iter__(self):
        for device in self.__devices:
            yield device

    def __len__(self):
        return len(self.__devices)
