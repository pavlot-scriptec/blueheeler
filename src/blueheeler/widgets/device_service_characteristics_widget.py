import gi

gi.require_version("Gtk", "4.0")
from gettext import gettext

from gi.repository import Gio, Gtk

_ = gettext


from ..models.adapters.blecharacteristicadapter import BleCharacteristicAdapter
from ..models.adapters.blecharacteristicdescriptoradapter import (
    BleCharacteristicDescriptorAdapter,
)
from ..models.adapters.bledevicecontroller import BleDeviceController
from ..models.adapters.bleserviceadapter import BleServiceAdapter
from .device_service_characteristic_descriptor_generic_widget import (
    DeviceServiceCharacteristicDescriptorGenericWidget,
)
from .device_service_characteristic_generic_widget import (
    DeviceServiceCharacteristicGenericWidget,
)


class DeviceServiceCharacteristicRowWidget:
    def __init__(self):
        self.label = Gtk.Label()
        self.expander = Gtk.TreeExpander()
        self.expander.set_child(self.label)


class DeviceServiceCharacteristicFactory(Gtk.SignalListItemFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect("setup", self.__on_factory_setup)
        self.connect("bind", self.__on_factory_bind)

    def __on_factory_setup(self, factory, list_item):
        row_widget = DeviceServiceCharacteristicRowWidget()
        list_item.set_child(row_widget.expander)
        list_item.row_widget = row_widget

    def __on_factory_bind(self, factory, list_item):
        tree_row = list_item.get_item()
        row_widget = list_item.row_widget
        model_item = tree_row.get_item()
        row_widget.expander.set_list_row(tree_row)

        if isinstance(model_item, BleCharacteristicAdapter):
            row_widget.label.set_text(model_item.description)
        if isinstance(model_item, BleCharacteristicDescriptorAdapter):
            row_widget.label.set_text(model_item.description)


class DeviceServiceCharacteristicsWidget(Gtk.Box):

    def __init__(self, device_controller: BleDeviceController, **kwargs):
        super().__init__(**kwargs)
        self.__device_controller: BleDeviceController = device_controller
        self.__build_ui()

    def load_characteristics(self, service: BleServiceAdapter):
        self.__store.remove_all()
        for characteristic in service.characteristics:
            self.__store.append(characteristic)
        self.__update_ui_for_selected_characteristic(self.__selection)

    def __add_tree_node(self, model_item):
        if isinstance(model_item, BleCharacteristicAdapter):
            descriptors = model_item.descriptors
            if not descriptors:
                return None
            store = Gio.ListStore.new(BleCharacteristicDescriptorAdapter)
            for descriptor in descriptors:
                store.append(descriptor)
            return store

    def __build_ui(self):
        self.__characteristics_detail_widget = Gtk.Box()
        self.__characteristics_detail_widget.set_hexpand(True)
        self.__characteristic_list = self.__build_characteristics_list()

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_start_child(self.__characteristic_list)
        paned.set_end_child(self.__characteristics_detail_widget)

        paned.set_shrink_start_child(False)
        paned.set_resize_start_child(False)

        self.append(paned)

    def __build_characteristics_list(self):
        container = Gtk.Box()
        container.set_hexpand(False)
        container.add_css_class("device-list")

        scrolled_window = Gtk.ScrolledWindow()
        container.append(scrolled_window)
        scrolled_window.set_propagate_natural_width(True)
        scrolled_window.set_propagate_natural_height(True)
        scrolled_window.props.vexpand = True

        column_view = Gtk.ColumnView()
        scrolled_window.set_child(column_view)
        factory = DeviceServiceCharacteristicFactory()
        self.__store = Gio.ListStore.new(BleCharacteristicAdapter)
        model = Gtk.TreeListModel.new(self.__store, False, False, self.__add_tree_node)

        self.__selection = Gtk.SingleSelection()
        self.__selection.set_model(model)
        self.__selection.connect("selection-changed", self.__on_selection_changed)

        column_view.set_model(self.__selection)

        column1 = Gtk.ColumnViewColumn.new("Characteristics", factory)
        column_view.append_column(column1)
        return container

    def __clear_characteristics_detail_widget(self):
        child = self.__characteristics_detail_widget.get_first_child()
        while child:
            self.__characteristics_detail_widget.remove(child)
            child = self.__characteristics_detail_widget.get_first_child()

    def __create_widgets_for_selected_characteristic(self, model):
        tree_row = model.get_selected_item()
        if tree_row:
            model_item = tree_row.get_item()

            if isinstance(model_item, BleCharacteristicAdapter):
                characteristic_widget = DeviceServiceCharacteristicGenericWidget(
                    self.__device_controller
                )
                characteristic_widget.characteristic = model_item  # type: ignore[method-assign]
                self.__characteristics_detail_widget.append(characteristic_widget)

            if isinstance(model_item, BleCharacteristicDescriptorAdapter):
                descriptor_widget = DeviceServiceCharacteristicDescriptorGenericWidget(
                    self.__device_controller
                )
                descriptor_widget.descriptor = model_item  # type: ignore[method-assign]
                self.__characteristics_detail_widget.append(descriptor_widget)

    def __update_ui_for_selected_characteristic(self, model):
        self.__clear_characteristics_detail_widget()
        self.__create_widgets_for_selected_characteristic(model)

    def __on_selection_changed(self, model, position, count):
        self.__update_ui_for_selected_characteristic(model)
