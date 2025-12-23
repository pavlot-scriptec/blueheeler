from __future__ import annotations

from typing import TYPE_CHECKING

from bleak.backends.service import BleakGATTServiceCollection
from gi.repository import GObject

# to prevent circular import
if TYPE_CHECKING:
    from blueheeler.models.adapters.bledeviceadapter import BleDeviceAdapter

from blueheeler.models.adapters.bleserviceadapter import BleServiceAdapter


class ServicesCollectionAdapter(GObject.Object):
    __gtype_name__ = "ServicesCollectionAdapter"

    def __init__(self, device:"BleDeviceAdapter", services: BleakGATTServiceCollection):
        super().__init__()
        self.__services: list[BleServiceAdapter] = []
        for service in services:
            self.__services.append(BleServiceAdapter(device, service))

    def __iter__(self):
        for service in self.__services:
            yield service

    def __len__(self):
        return len(self.__services)