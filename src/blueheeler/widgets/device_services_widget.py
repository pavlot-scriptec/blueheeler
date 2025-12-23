import gi

gi.require_version("Gtk", "4.0")
from gettext import gettext

from gi.repository import Gtk

_ = gettext

from typing import Union

from ..models.adapters.bledevicecontroller import BleDeviceController
from .common.image_label import ImageLabel
from .generic_service_page import GenericServicePage


class DeviceServicesWidget(Gtk.Box):
    def __init__(self, device_controller: BleDeviceController, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__central_widget: Union[Gtk.Notebook, Gtk.Box, None] = None
        device_controller.device_adapter.connect(
            "notify::services",
            lambda sender, services: self.__on_services_changed(device_controller),
        )
        self.__update_ui(device_controller=device_controller)

    def __update_ui(self, device_controller: BleDeviceController):
        if self.__central_widget:
            self.remove(self.__central_widget)
            del self.__central_widget
            self.__central_widget = None
        self.__central_widget = self.__build_central_widget(device_controller=device_controller)
        self.__central_widget.props.hexpand = True
        self.__central_widget.props.vexpand = True
        self.append(self.__central_widget)

    def __build_central_widget(self, device_controller: BleDeviceController) -> Gtk.Notebook | Gtk.Box:
        if device_controller.device_adapter.services is None:
            central_widget = Gtk.Box(
                spacing=6, orientation=Gtk.Orientation.VERTICAL, homogeneous=True
            )
            central_widget.append(Gtk.Label(label=_("Services are loading")))
            spinner = Gtk.Spinner()
            central_widget.append(spinner)
            spinner.start()
            return central_widget
        if len(device_controller.device_adapter.services)==0:
            central_widget = Gtk.Box(
                spacing=6, orientation=Gtk.Orientation.VERTICAL, homogeneous=True
            )
            central_widget.append(Gtk.Label(label=_("No services detected on device")))
            return central_widget

        return self.__build_device_adapter_services_notebook(device_controller)

    def __build_device_adapter_services_notebook(
        self, device_controller: BleDeviceController
    ) -> Gtk.Notebook:
        if not device_controller.device_adapter.services:
            raise RuntimeError("Unable to create service notebook. Service list is empty.")

        notebook = Gtk.Notebook()
        notebook.props.scrollable = True
        self.__build_services_pages(notebook, device_controller)
        return notebook

    def __build_services_pages(
        self, notebook: Gtk.Notebook, device_controller: BleDeviceController
    ):
        for service in sorted(device_controller.device_adapter.services, key=lambda item: item.handle):
            page = GenericServicePage(device_controller)
            page.service = service # type: ignore[method-assign]
            page_title = ImageLabel()
            page_title.label.props.label = service.description
            page_title.image.props.icon_name = "preferences-system"
            notebook.append_page(page, page_title)

    def __on_services_changed(self, device_controller:BleDeviceController):
        self.__update_ui(device_controller=device_controller)
        return True
