from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")

from typing import TYPE_CHECKING

from bleak.backends.descriptor import BleakGATTDescriptor
from gi.repository import GObject

# to prevent circular import
if TYPE_CHECKING:
    from blueheeler.models.adapters.blecharacteristicadapter import (
        BleCharacteristicAdapter,
    )


class BleCharacteristicDescriptorAdapter(GObject.Object):
    __gtype_name__ = "BleCharacteristicDescriptorAdapter"

    def __init__(
        self, characteristic: BleCharacteristicAdapter, descriptor: BleakGATTDescriptor
    ):
        super().__init__()
        self.__characteristic: BleCharacteristicAdapter = characteristic
        self.__descriptor: BleakGATTDescriptor = descriptor

    ################################################################################################
    # Properties
    ################################################################################################

    @GObject.Property(type=GObject.TYPE_PYOBJECT)  # type: ignore[arg-type]
    def characteristic(self) -> BleCharacteristicAdapter:
        return self.__characteristic

    @GObject.Property(type=str)
    def uuid(self):
        return self.__descriptor.uuid

    @GObject.Property(type=int)
    def handle(self):
        return self.__descriptor.handle

    @GObject.Property(type=str)
    def characteristic_uuid(self):
        return self.__descriptor.characteristic_uuid

    @GObject.Property(type=int)
    def characteristic_handle(self):
        return self.__descriptor.characteristic_handle

    @GObject.Property(type=str)
    def description(self):
        return self.__descriptor.description

    def get_descriptor(self):
        return self.__descriptor


# ---------------------------------------------------------------------------------------------------


class CharacteristicDescriptorsCollectionAdapter(GObject.Object):
    __gtype_name__ = "CharacteristicDescriptorsCollectionAdapter"

    def __init__(
        self,
        characteristic: BleCharacteristicAdapter,
        descriptors: list[BleakGATTDescriptor],
    ):
        super().__init__()
        self.__descriptors: list[BleCharacteristicDescriptorAdapter] = []
        for descriptor in descriptors:
            self.__descriptors.append(
                BleCharacteristicDescriptorAdapter(characteristic, descriptor)
            )

    def __iter__(self):
        for descriptor in self.__descriptors:
            yield descriptor

    def __len__(self):
        return len(self.__descriptors)
