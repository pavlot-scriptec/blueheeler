import gi

gi.require_version("Gtk", "4.0")
import logging
from asyncio import Event, Lock, Task, create_task
from typing import Optional

from bleak import BleakScanner
from gi.repository import GObject

from ..models.adapters.bledeviceadapter import BleDeviceAdapter


# TODO PTAR Add shared lock to this task
# TODO PTAR Maybe refactor to some common task parent
# TODO PTAR Maybe it should be renamed to device collector
class CollectDevicesTask(GObject.Object):

    __gtype_name__ = "CollectDevicesTask"

    def __init__(self, lock:Lock):
        super().__init__()
        self.__task: Optional[Task] = None
        self.__scanning_stop_event:Event = Event()
        self.__lock:Lock = Lock()

    def start(self):
        self.__scanning_stop_event = Event()
        if self.__task is not None:
            logging.warning("Task already running")
            return
        self.__task = create_task(self._run())
        self.__task.add_done_callback(self.__task_is_done)
        self.notify("is-active")

    def stop(self):
        self.__scanning_stop_event.set()

    async def _run(self):
        def callback(device, advertising_data):
            self.emit("signal_new_device_discovered", BleDeviceAdapter(device))

        async with self.__lock:
            async with BleakScanner(callback) as _:
                await self.__scanning_stop_event.wait()

    ################################################################################################
    # Properties
    ################################################################################################

    @GObject.Property(type=bool, default=False)
    def is_active(self):
        return self.__task is not None

    ################################################################################################
    # Signals
    ################################################################################################
    @GObject.Signal
    def signal_new_device_discovered(self, device: BleDeviceAdapter):
        logging.debug("signal_new_device_discovered")

    def __task_is_done(self, future):
        self.__task = None
        self.notify("is-active")
