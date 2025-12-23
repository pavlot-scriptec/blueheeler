from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")


from typing import TYPE_CHECKING

from bleak.backends.service import BleakGATTService
from gi.repository import GObject

if TYPE_CHECKING:
    from blueheeler.models.adapters.bledeviceadapter import BleDeviceAdapter

from .blecharacteristicadapter import CharacteristicsCollectionAdapter


class BleServiceAdapter(GObject.Object):
    __gtype_name__ = "BleServiceAdapter"

    def __init__(self, device:BleDeviceAdapter, service: BleakGATTService):
        super().__init__()
        self.__device:BleDeviceAdapter = device 
        self.__service: BleakGATTService = service
        self.__characteristics = CharacteristicsCollectionAdapter(self, self.__service.characteristics)

    ################################################################################################
    # Properties
    ################################################################################################

    @GObject.Property(type=GObject.TYPE_PYOBJECT) # type: ignore[arg-type]
    def device(self)->BleDeviceAdapter:
        return self.__device

    @GObject.Property(type=GObject.TYPE_PYOBJECT)  # type: ignore[arg-type]
    def service(self) -> BleakGATTService:
        return self.__service

    @GObject.Property(type=str)
    def uuid(self)->str:
        return self.__service.uuid

    @GObject.Property(type=int)
    def handle(self)->int:
        return self.__service.handle

    @GObject.Property(type=str)
    def description(self)->str:
        return self.__service.description

    # @GObject.Property(type=bool, default=True)
    # def is_primary(self):
    #     return self.__service.is_primary

    # @GObject.Property(type=object)
    # def includes(self):
    #     return self.__service.includes

    @GObject.Property(type=CharacteristicsCollectionAdapter)
    def characteristics(self):
        return self.__characteristics


