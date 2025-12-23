import gi

gi.require_version("Gtk", "4.0")
import logging
from typing import Optional

from gi.repository import GObject

from blueheeler.models.adapters.blecharacteristicdescriptoradapter import (
    BleCharacteristicDescriptorAdapter,
)

from .client_task import ClientTask


class ReadDescriptorTask(ClientTask):

    __gtype_name__ = "ReadDescriptorTask"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__descriptor: Optional[BleCharacteristicDescriptorAdapter] = None

    async def _run(self):
        if self.__descriptor is None: 
            raise RuntimeError("Unable to run task with descriptor==None")

        data = await self._client.read_gatt_descriptor(self.__descriptor.get_descriptor())
        self.emit("signal_data_received", data)

    ################################################################################################
    # Properties
    ################################################################################################
    @GObject.Property(type=BleCharacteristicDescriptorAdapter)
    def descriptor(self):
        return self.__descriptor

    @descriptor.setter # type: ignore[no-redef]
    def descriptor(self, descriptor: BleCharacteristicDescriptorAdapter):
        self.__descriptor = descriptor

    ################################################################################################
    # Signals
    ################################################################################################
    @GObject.Signal(arg_types=(GObject.TYPE_PYOBJECT,))# type: ignore[arg-type]
    def signal_data_received(self, data: bytearray):
        logging.debug("signal_data_received: {}".format(data))
