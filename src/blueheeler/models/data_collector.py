import gi

gi.require_version("GLib", "2.0")
gi.require_version("GObject", "2.0")
import logging

from gi.repository import Gio, GObject

from blueheeler.models.adapters.blecharacteristicadapter import BleCharacteristicAdapter
from blueheeler.models.adapters.blecharacteristicdescriptoradapter import (
    BleCharacteristicDescriptorAdapter,
)
from blueheeler.models.data_packet import DataPacket


class DataCollector(GObject.Object):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__data_store = Gio.ListStore(item_type=DataPacket)

    def collect_characteristic_data(self, sender:BleCharacteristicAdapter|BleCharacteristicDescriptorAdapter, is_incoming, data):
        logging.info("TODO PTAR REMOVE IT. Data collected: {}".format(data))
        if isinstance(sender, BleCharacteristicAdapter):
            packet = DataPacket(sender, None, is_incoming, data)
            self.__data_store.append(packet)
        elif isinstance(sender, BleCharacteristicDescriptorAdapter):
            packet = DataPacket(sender.characteristic, sender, is_incoming, data)
            self.__data_store.append(packet)

    ################################################################################################
    # Properties
    ################################################################################################
    @GObject.Property(type=Gio.ListStore)
    def data_store(self) -> Gio.ListStore:
        return self.__data_store
