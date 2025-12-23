import gi

gi.require_version("Gtk", "4.0")
from gettext import gettext

from gi.repository import GObject, Gtk

_ = gettext

import logging

from blueheeler.models.adapters.bledeviceadapter import BleDeviceAdapter
from blueheeler.models.device_repository import DeviceRepository


class DeviceRowWidget(Gtk.Box):

    def __init__(self, factory, list_item, **kwargs):
        super().__init__(**kwargs)
        self.props.spacing = 6
        self.props.orientation = Gtk.Orientation.VERTICAL
        self.__factory = factory
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)

        self.label_address = Gtk.Label()
        self.append(self.label_address)

        self.label_name = Gtk.Label()
        self.append(self.label_name)

        self.gesture = Gtk.GestureClick()
        self.gesture.set_button(0)  # 0 = any mouse button
        self.gesture.connect("released", self.__on_item_doubleclick, list_item)
        self.add_controller(self.gesture)

    def __on_item_doubleclick(self, gesture, n_press, x, y, list_item):
        if n_press == 2:
            device_adapter = list_item.get_item()
            self.__factory.emit("signal_device_selected", device_adapter)

class DeviceListViewFactory(Gtk.SignalListItemFactory):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect("setup", self._on_factory_setup)
        self.connect("bind", self._on_factory_bind)

    def _on_factory_setup(self, factory, list_item):
        cell: DeviceRowWidget = DeviceRowWidget(self, list_item)
        list_item.set_child(cell)
        
    def _on_factory_bind(self, factory, list_item):
        cell: DeviceRowWidget = list_item.get_child()
        device_adapter = list_item.get_item()
        cell.label_address.set_text(device_adapter.address)
        cell.label_name.set_text(device_adapter.name)

    ################################################################################################
    # Signals
    ################################################################################################
    @GObject.Signal
    def signal_device_selected(self, device_adapter:BleDeviceAdapter):
        logging.debug("signal_device_selected: {}".format(device_adapter))



class ScanForDevicesDialog(Gtk.Window):
    def __init__(self, parent, device_repository: DeviceRepository):
        super().__init__(
            title=_("Scanning for devices"), transient_for=parent, modal=True
        )
        self.__device_repository:DeviceRepository = device_repository

        self.set_default_size(300, 200)

        self.__build_ui()
        self.__connect_signals()

    def __build_ui(self):
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )

        factory = DeviceListViewFactory()
        factory.connect("signal_device_selected",self.__on_device_selected)
        selection_model = Gtk.SingleSelection(model=self.__device_repository.devices)

        self.__list_liew_devices = Gtk.ListView(model=selection_model, factory=factory)
        self.__list_liew_devices.props.vexpand = True
        self.__list_liew_devices.props.single_click_activate = True
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_propagate_natural_height(True)
        scrolled_window.add_css_class("device-list")
        scrolled_window.set_child(self.__list_liew_devices)
        scrolled_window.props.vexpand = True
        box.append(scrolled_window)

        self.close_button = Gtk.Button(label=_("Close"))
        box.append(self.close_button)

        self.set_child(box)

    def __connect_signals(self):
        self.connect("show", self.__on_show)
        self.connect("close-request", self.__on_close_request)
        self.close_button.connect("clicked", self.__on_close_clicked)

    def __on_close_clicked(self, button):
        self.close()
    
    def __on_show(self, dialog):
        self.__device_repository.start_collect_devices()

    def __on_close_request(self, dialog):
        self.__device_repository.stop_collect_devices()
        return False

    def __on_device_selected(self, factory, device_adapter:BleDeviceAdapter):
        self.emit("signal_device_selected", device_adapter)
        self.close()

    ################################################################################################
    # Properties
    ################################################################################################
    @GObject.Property(type=Gtk.ListView)
    def list_liew_devices(self):
        return self.__list_liew_devices


    ################################################################################################
    # Signals
    ################################################################################################
    @GObject.Signal
    def signal_device_selected(self, device_adapter:BleDeviceAdapter):
        logging.debug("signal_device_selected: {}".format(device_adapter))

