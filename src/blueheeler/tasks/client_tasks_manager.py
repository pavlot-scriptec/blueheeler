import gi

gi.require_version("Gtk", "4.0")

from asyncio import Task, create_task

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from gi.repository import GObject


class ClientTasksManager(GObject.Object):

    __gtype_name__ = "ClientTasksManager"

    # TODO PTAR Add parameter shared lock
    def __init__(self, device:BLEDevice):
        super().__init__()
        self.__tasks:list[Task] = []
        self.__active_tasks_count: int = 0
        # TODO PTAR Client has to be shared between tasks, so for each device separate client has to be created and stored to the dict
        self.__client =  BleakClient(device)
    
    def __del__(self):
        # TODO PTAR Remove all tasks here?
        if self.__client.is_connected:
            create_task(self.__client.disconnect())

    def create_managed_client_task(self, task_class):
        task = task_class(self.__client, self)
        self.__tasks.append(task)
        task.connect("notify::is-active", self.__on_active_state_change)
        return task

    def __on_active_state_change(self, task, property_spec):
        if task.is_active:
            self.__active_tasks_count += 1
        else:
            self.__active_tasks_count -= 1
        self.notify("active-tasks-count")

    ################################################################################################
    # Properties
    ################################################################################################
    @GObject.Property(type=int)
    def active_tasks_count(self):
        return self.__active_tasks_count

    ################################################################################################
    # Signals
    ################################################################################################
