import gi

gi.require_version("Gtk", "4.0")
import logging
from asyncio import Lock, Task, create_task
from typing import Optional

from bleak import BleakClient
from gi.repository import GObject


class ClientTask(GObject.Object):

    __gtype_name__ = "ClientTask"

    def __init__(self, client: BleakClient, client_lock:Lock):
        super().__init__()
        self.__task:Optional[Task] = None
        self._client = client
        self._client_lock = client_lock

    def start(self):
        logging.info(
            "TODO PTAR Remove it. TASK IS STARTING"
        )

        if self.__task is not None:
            logging.warning("Task already running")
            return
        self.__task = create_task(self._run_connected())
        self.__task.add_done_callback(self._task_is_done)
        self.notify("is-active")

    def stop(self):
        if self.__task is None:
            logging.warning("No running task to stop")
            return
        self.__task.cancel()

    async def _run_connected(self):
        await self.__connect_client_if_required()
        await self._run()
        
    async def _run(self):
        raise RuntimeError("Run function is not implemented")

    async def __connect_client_if_required(self):
        if self._client.is_connected:
            return
        async with self._client_lock:
            await self._client.connect()
        
    def _task_is_done(self, future):
        logging.info(
            "TODO PTAR Remove it. TASK IS DONE"
        )
        self.__task = None
        self.notify("is-active")

    ################################################################################################
    # Properties
    ################################################################################################
    @GObject.Property(type=bool, default=False)
    def is_active(self):
        return self.__task is not None

    ################################################################################################
    # Signals
    ################################################################################################
