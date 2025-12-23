import gi

gi.require_version("Gtk", "4.0")
import logging
from asyncio import Lock, create_task
from typing import Optional

from bleak import BleakGATTCharacteristic
from gi.repository import GObject

from blueheeler.models.adapters.blecharacteristicadapter import BleCharacteristicAdapter

from .client_task import ClientTask


class NotifyCharacteristicTask(ClientTask):

    __gtype_name__ = "NotifyCharacteristicTask"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__lock:Lock = Lock()
        self.__is_active:bool = False
        self.__characteristic: Optional[BleCharacteristicAdapter] = None

    def start(self):
        create_task(self._run_connected())

    def stop(self):
        create_task(self.__stop_async())

    async def __stop_async(self):
        if self.__characteristic is None:
            return
        async with self.__lock:
            if not self.is_active:
                logging.warning("No running task to stop")
                return
            await self._client.stop_notify(self.__characteristic.get_characteristic())
            self.is_active = False# type: ignore[method-assign]

    async def _run(self):
        if self.__characteristic is None:
            raise RuntimeError("Unable to run task with characteristic==None")
        async with self.__lock:
            if self.is_active:
                logging.warning("Task already running")
                return
            await self._client.start_notify(self.__characteristic.get_characteristic(), self.__on_data_received)
            self.is_active = True# type: ignore[method-assign]

    def __on_data_received(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        self.emit("signal_data_received", data)

    ################################################################################################
    # Properties
    ################################################################################################
    @GObject.Property(type=bool, default=False)
    def is_active(self):
        return self.__is_active

    @is_active.setter # type: ignore[no-redef]
    def is_active(self, value):
        self.__is_active = value
    
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
