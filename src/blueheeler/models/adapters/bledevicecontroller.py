import gi

gi.require_version("Gtk", "4.0")
import logging
from asyncio import Lock, create_task

from bleak import BleakClient
from gi.repository import GObject

from blueheeler.models.adapters.blecharacteristicadapter import BleCharacteristicAdapter
from blueheeler.models.adapters.blecharacteristicdescriptoradapter import (
    BleCharacteristicDescriptorAdapter,
)
from blueheeler.models.adapters.bledeviceadapter import BleDeviceAdapter
from blueheeler.tasks.load_device_services_task import LoadDeviceServicesTask
from blueheeler.tasks.notify_characteristic_task import NotifyCharacteristicTask
from blueheeler.tasks.read_characteristic_task import ReadCharacteristicTask
from blueheeler.tasks.read_descriptor_task import ReadDescriptorTask
from blueheeler.tasks.write_characteristic_task import WriteCharacteristicTask
from blueheeler.tasks.write_descriptor_task import WriteDescriptorTask


class BleDeviceController(GObject.GObject):
    def __init__(self, device_adapter: BleDeviceAdapter, shared_lock: Lock, **kwargs):
        super().__init__(**kwargs)
        self.__device_adapter: BleDeviceAdapter = device_adapter
        self.__shared_lock: Lock = shared_lock  # TODO PTAR Is it required still?
        self.__client_lock: Lock = Lock()
        self.__client: BleakClient = BleakClient(self.__device_adapter.get_device())
        self.__load_services_task = LoadDeviceServicesTask(
            self.__device_adapter, self.__client, self.__client_lock
        )
        self.__load_services_task.connect(
            "signal_services_are_loaded", self.__on_signal_services_are_loaded
        )
        self.__read_characteristic_tasks: dict = {}
        self.__read_descriptor_tasks: dict = {}
        self.__write_characteristic_tasks: dict = {}
        self.__write_descriptor_tasks: dict = {}
        self.__notify_characteristic_tasks: dict = {}

    # def __del__(self):
    #     self.release()

    def release(self):
        # TODO PTAR Stop all running tasks, disconnect must be guarded
        if self.__client is not None:
            if self.__client.is_connected:
                create_task(self.__client.disconnect())
        self.emit("signal_released")

    @GObject.Property(type=BleDeviceAdapter)
    def device_adapter(self):
        return self.__device_adapter

    @GObject.Property(type=bool, default=False)
    def connected(self):
        return self.__client is not None and self.__client.is_connected

    @GObject.Property(type=LoadDeviceServicesTask)
    def load_services_task(self):
        return self.__load_services_task

    def read_characteristic(self, characteristic: BleCharacteristicAdapter):
        if characteristic in self.__read_characteristic_tasks:
            logging.info("Task read characteristic already running")
            return
        task = ReadCharacteristicTask(self.__client, self.__client_lock)
        task.characteristic = characteristic  # type: ignore[method-assign]
        task.connect("signal_data_received", self.__on_signal_data_received)
        task.connect("notify::is-active", self.__on_task_active_state_change)
        self.__read_characteristic_tasks[characteristic] = task
        logging.info(self.__read_characteristic_tasks)
        task.start()
        return task

    def read_descriptor(self, descriptor: BleCharacteristicDescriptorAdapter):
        if descriptor in self.__read_descriptor_tasks:
            logging.info("Task read descriptor already running")
            return
        task = ReadDescriptorTask(self.__client, self.__client_lock)
        task.descriptor = descriptor  # type: ignore[method-assign]
        task.connect("signal_data_received", self.__on_signal_data_received)
        task.connect("notify::is-active", self.__on_task_active_state_change)
        self.__read_descriptor_tasks[descriptor] = task
        logging.info(self.__read_descriptor_tasks)
        task.start()
        return task

    def write_characteristic(self, characteristic: BleCharacteristicAdapter, data):
        if characteristic in self.__write_characteristic_tasks:
            logging.info("Task write characteristic already running")
            return
        task = WriteCharacteristicTask(self.__client, self.__client_lock)
        task.characteristic = characteristic  # type: ignore[method-assign]
        task.data = data  # type: ignore[method-assign]
        task.connect("signal_data_sent", self.__on_signal_data_sent)
        task.connect("notify::is-active", self.__on_task_active_state_change)
        self.__write_characteristic_tasks[characteristic] = task
        logging.info(self.__write_characteristic_tasks)
        task.start()
        return task

    def write_descriptor(self, descriptor: BleCharacteristicDescriptorAdapter, data):
        if descriptor in self.__write_descriptor_tasks:
            logging.info("Task write descriptor already running")
            return
        task = WriteDescriptorTask(self.__client, self.__client_lock)
        task.descriptor = descriptor  # type: ignore[method-assign]
        task.data = data  # type: ignore[method-assign]
        task.connect("signal_data_sent", self.__on_signal_data_sent)
        task.connect("notify::is-active", self.__on_task_active_state_change)
        self.__write_descriptor_tasks[descriptor] = task
        logging.info(self.__write_descriptor_tasks)
        task.start()
        return task

    def start_notify_read(self, characteristic: BleCharacteristicAdapter):
        if characteristic in self.__notify_characteristic_tasks:
            logging.info("Task notify characteristic already running")
            return
        task = NotifyCharacteristicTask(self.__client, self.__client_lock)
        task.characteristic = characteristic  # type: ignore[method-assign]
        task.connect("signal_data_received", self.__on_signal_data_received)
        task.connect("notify::is-active", self.__on_task_active_state_change)
        self.__notify_characteristic_tasks[characteristic] = task
        task.start()
        return task

    def stop_notify_read(self, characteristic: BleCharacteristicAdapter):
        if characteristic not in self.__notify_characteristic_tasks:
            logging.info("Task notify characteristic is not running")
            return
        self.__notify_characteristic_tasks[characteristic].stop()

    def write(self):
        raise RuntimeError("{} not implemented yet".format(__name__))

    ################################################################################################
    # Signal handlers
    ################################################################################################

    def __on_signal_services_are_loaded(self, sender, services):
        self.__device_adapter.services = services  # type: ignore[method-assign]

    def __on_signal_data_received(self, sender, data):
        logging.info("Data received: {} {}".format(sender, data))
        if isinstance(sender, ReadCharacteristicTask) or isinstance(
            sender, NotifyCharacteristicTask
        ):
            self.emit(
                "signal_characteristic_data_received", sender.characteristic, data
            )
        if isinstance(sender, ReadDescriptorTask):
            self.emit("signal_descriptor_data_received", sender.descriptor, data)

    def __on_signal_data_sent(self, sender, data):
        logging.info("Data received: {} {}".format(sender, data))
        if isinstance(sender, WriteCharacteristicTask):
            self.emit("signal_characteristic_data_sent", sender.characteristic, data)
        if isinstance(sender, WriteDescriptorTask):
            self.emit("signal_descriptor_data_sent", sender.descriptor, data)

    def __on_task_active_state_change(self, task, property_spec):
        if not task.is_active:
            if isinstance(task, ReadCharacteristicTask):
                del self.__read_characteristic_tasks[task.characteristic]
            if isinstance(task, ReadDescriptorTask):
                del self.__read_descriptor_tasks[task.descriptor]
            if isinstance(task, NotifyCharacteristicTask):
                del self.__notify_characteristic_tasks[task.characteristic]
            if isinstance(task, WriteCharacteristicTask):
                del self.__write_characteristic_tasks[task.characteristic]
            if isinstance(task, WriteDescriptorTask):
                del self.__write_descriptor_tasks[task.descriptor]

    ################################################################################################
    # Signals
    ################################################################################################
    @GObject.Signal(arg_types=(BleCharacteristicAdapter, GObject.TYPE_PYOBJECT))  # type: ignore[arg-type]
    def signal_characteristic_data_received(
        self, characteristic: BleCharacteristicAdapter, data: bytearray
    ):
        logging.debug("signal_characteristic_data_received")

    @GObject.Signal(arg_types=(BleCharacteristicAdapter, GObject.TYPE_PYOBJECT))  # type: ignore[arg-type]
    def signal_characteristic_data_sent(
        self, characteristic: BleCharacteristicAdapter, data: bytearray
    ):
        logging.debug("signal_characteristic_data_sent")

    @GObject.Signal(arg_types=(BleCharacteristicDescriptorAdapter, GObject.TYPE_PYOBJECT))  # type: ignore[arg-type]
    def signal_descriptor_data_received(
        self, characteristic: BleCharacteristicDescriptorAdapter, data: bytearray
    ):
        logging.debug("signal_characteristic_data_received")

    @GObject.Signal(arg_types=(BleCharacteristicDescriptorAdapter, GObject.TYPE_PYOBJECT))  # type: ignore[arg-type]
    def signal_descriptor_data_sent(
        self, characteristic: BleCharacteristicDescriptorAdapter, data: bytearray
    ):
        logging.debug("signal_characteristic_data_sent")

    @GObject.Signal()  # type: ignore[arg-type]
    def signal_released(self):
        logging.debug("signal_released")
