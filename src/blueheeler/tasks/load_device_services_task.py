import gi

gi.require_version("Gtk", "4.0")
import logging

from gi.repository import GObject

from blueheeler.models.adapters.bledeviceadapter import BleDeviceAdapter
from blueheeler.models.adapters.services_collection_adapter import ServicesCollectionAdapter

from .client_task import ClientTask


class LoadDeviceServicesTask(ClientTask):

    __gtype_name__ = "LoadDeviceServicesTask"

    def __init__(self, device_adapter: BleDeviceAdapter, client, client_lock):
        super().__init__(client, client_lock)
        self.__device_adapter: BleDeviceAdapter = device_adapter

    async def _run(self):
        self.emit("signal_services_are_loaded", ServicesCollectionAdapter(self.__device_adapter, self._client.services))

    ################################################################################################
    # Properties
    ################################################################################################

    ################################################################################################
    # Signals
    ################################################################################################
    @GObject.Signal
    def signal_services_are_loaded(self, services: ServicesCollectionAdapter):
        logging.debug("signal_services_are_loaded")
