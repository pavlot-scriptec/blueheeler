from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")

from typing import TYPE_CHECKING

from bleak.backends.characteristic import BleakGATTCharacteristic
from gi.repository import GObject

from .blecharacteristicdescriptoradapter import (
    CharacteristicDescriptorsCollectionAdapter,
)

# to prevent circular import
if TYPE_CHECKING:
    from blueheeler.models.adapters.bleserviceadapter import BleServiceAdapter


class BleCharacteristicAdapter(GObject.Object):
    __gtype_name__ = "BleCharacteristicAdapter"

    def __init__(
        self, service: BleServiceAdapter, characteristic: BleakGATTCharacteristic
    ):
        super().__init__()
        self.__service: BleServiceAdapter = service
        self.__characteristic: BleakGATTCharacteristic = characteristic
        self.__descriptors: CharacteristicDescriptorsCollectionAdapter = (
            CharacteristicDescriptorsCollectionAdapter(
                self, self.__characteristic.descriptors
            )
        )

    def get_characteristic(self):
        return self.__characteristic

    ################################################################################################
    # Properties
    ################################################################################################

    @GObject.Property(type=GObject.TYPE_PYOBJECT)  # type: ignore[arg-type]
    def service(self) -> BleServiceAdapter:
        return self.__service

    @GObject.Property(type=GObject.TYPE_PYOBJECT)  # type: ignore[arg-type]
    def characteristic(self) -> BleakGATTCharacteristic:
        return self.__characteristic

    @GObject.Property(type=str)
    def uuid(self) -> str:
        return self.__characteristic.uuid

    @GObject.Property(type=int)
    def handle(self) -> int:
        return self.__characteristic.handle

    @GObject.Property(type=str)
    def description(self) -> str:
        return self.__characteristic.description

    @GObject.Property(type=object)
    def properties(self) -> list:
        return self.__characteristic.properties

    @GObject.Property(type=str)
    def service_uuid(self) -> str:
        return self.__characteristic.service_uuid

    @GObject.Property(type=CharacteristicDescriptorsCollectionAdapter)
    def descriptors(self) -> CharacteristicDescriptorsCollectionAdapter:
        return self.__descriptors


class CharacteristicsCollectionAdapter(GObject.Object):
    __gtype_name__ = "CharacteristicsCollectionAdapter"

    def __init__(
        self, service: BleServiceAdapter, characteristics: list[BleakGATTCharacteristic]
    ):
        super().__init__()
        self.__characteristics: list[BleCharacteristicAdapter] = []
        for characteristic in characteristics:
            self.__characteristics.append(
                BleCharacteristicAdapter(service, characteristic)
            )

    def __iter__(self):
        for characteristic in self.__characteristics:
            yield characteristic

    def __len__(self):
        return len(self.__characteristics)
