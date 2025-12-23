import gi

gi.require_version("Gtk", "4.0")
import logging
from typing import Optional

from gi.repository import GLib, GObject

from blueheeler.models.adapters.blecharacteristicadapter import BleCharacteristicAdapter

from .client_task import ClientTask


class WriteCharacteristicTask(ClientTask):

    __gtype_name__ = "WriteCharacteristicTask"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__characteristic: Optional[BleCharacteristicAdapter] = None
        self.__data: Optional[GLib.Bytes] = None

    async def _run(self):
        if self.__characteristic is None: 
            raise RuntimeError("Unable to run task with characteristic==None")
        if self.__data is None:
            raise RuntimeError("Unable to run task with data==None")
        
        data = self.__data.get_data()
        if data:
            await self._client.write_gatt_char(self.__characteristic.get_characteristic(), data)
            self.emit("signal_data_sent", data)

    ################################################################################################
    # Properties
    ################################################################################################
    @GObject.Property(type=BleCharacteristicAdapter)
    def characteristic(self):
        return self.__characteristic

    @characteristic.setter # type: ignore[no-redef]
    def characteristic(self, characteristic: BleCharacteristicAdapter):
        self.__characteristic = characteristic

    @GObject.Property(type=GLib.Bytes)
    def data(self):
        return self.__data

    @data.setter # type: ignore[no-redef]
    def data(self, value):
        self.__data = value

    ################################################################################################
    # Signals
    ################################################################################################
    @GObject.Signal(arg_types=(GObject.TYPE_PYOBJECT,))# type: ignore[arg-type]
    def signal_data_sent(self, data: bytearray):
        logging.debug("signal_data_sent: {}".format(data))
