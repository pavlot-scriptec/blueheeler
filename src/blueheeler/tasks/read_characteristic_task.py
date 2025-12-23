import gi

gi.require_version("Gtk", "4.0")
import logging
from typing import Optional

from gi.repository import GObject

from blueheeler.models.adapters.blecharacteristicadapter import BleCharacteristicAdapter

from .client_task import ClientTask


class ReadCharacteristicTask(ClientTask):

    __gtype_name__ = "ReadCharacteristicTask"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__characteristic: Optional[BleCharacteristicAdapter] = None

    async def _run(self):
        if self.__characteristic is None: 
            raise RuntimeError("Unable to run task with characteristic==None")

        data = await self._client.read_gatt_char(self.__characteristic.get_characteristic())
        self.emit("signal_data_received", data)

    ################################################################################################
    # Properties
    ################################################################################################
    @GObject.Property(type=BleCharacteristicAdapter)
    def characteristic(self):
        return self.__characteristic

    @characteristic.setter # type: ignore[no-redef]
    def characteristic(self, characteristic: BleCharacteristicAdapter):
        self.__characteristic = characteristic

    ################################################################################################
    # Signals
    ################################################################################################
    @GObject.Signal(arg_types=(GObject.TYPE_PYOBJECT,))# type: ignore[arg-type]
    def signal_data_received(self, data: bytearray):
        logging.debug("signal_data_received: {}".format(data))
