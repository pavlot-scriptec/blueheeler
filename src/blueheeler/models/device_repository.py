import gi

gi.require_version("Gtk", "4.0")
from asyncio import Lock

from gi.repository import GObject

from blueheeler.models.adapters.bledeviceadapter import BleDeviceAdapter
from blueheeler.models.adapters.bledevicecontroller import BleDeviceController
from blueheeler.models.deviceliststore import DeviceListStore
from blueheeler.tasks.collect_devices_task import CollectDevicesTask


class DeviceRepository(GObject.GObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__lock: Lock = Lock()
        self.__devices: DeviceListStore = DeviceListStore()
        self.__device_controllers: dict[str, BleDeviceController] = {}
        self.__collect_devices_task = CollectDevicesTask(self.__lock)
        self.__collect_devices_task.connect(
            "signal_new_device_discovered", self.__on_new_device_discovered
        )

    def start_collect_devices(self):
        self.__collect_devices_task.start()

    def stop_collect_devices(self):
        self.__collect_devices_task.stop()

    def __on_new_device_discovered(
        self, sender: CollectDevicesTask, device_adapter: BleDeviceAdapter
    ):
        self.__devices.append_or_update(device_adapter)

    def get_or_create_device_controller(self, device_adapter: BleDeviceAdapter):
        is_created = False
        if device_adapter.address not in self.__device_controllers:
            self.__device_controllers[device_adapter.address] = BleDeviceController(
                device_adapter=device_adapter, shared_lock=self.__lock
            )
            is_created = True
            self.__device_controllers[device_adapter.address].connect("signal_released", self.__on_signal_released)
        return self.__device_controllers[device_adapter.address], is_created

    ################################################################################################
    # Properties
    ################################################################################################

    @GObject.Property(type=DeviceListStore)
    def devices(self):
        return self.__devices

    ################################################################################################
    # Signal handlers
    ################################################################################################

    def __on_signal_released(self, device_controller):
        del self.__device_controllers[device_controller.device_adapter.address]

    ################################################################################################
    # Signals
    ################################################################################################
