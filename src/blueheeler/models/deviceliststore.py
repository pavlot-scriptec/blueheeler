import gi

gi.require_version("Gtk", "4.0")
import logging

from gi.repository import Gio

from .adapters.bledeviceadapter import BleDeviceAdapter


class DeviceListStore(Gio.ListStore):
    def __init__(self, *args, **kwargs):
        kwargs["item_type"]=BleDeviceAdapter
        super().__init__(*args, **kwargs)
        self.__devices: dict[str, BleDeviceAdapter] = {}

    def append_or_update(self, device: BleDeviceAdapter):
        if not device.address:
            logging.error(f"Received update for device without address: {device}")
            return
        if device.address not in self.__devices:
            self.__devices[device.address] = device
            self.append(self.__devices[device.address])
            return
        # TODO Rethink how properly update it
        self.__devices[device.address].update(device.get_device())
