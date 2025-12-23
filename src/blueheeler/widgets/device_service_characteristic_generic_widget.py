import gi

gi.require_version("Gtk", "4.0")
from gettext import gettext

from gi.repository import GObject, Gtk

_ = gettext


from typing import Optional

from blueheeler.models.adapters.bledevicecontroller import BleDeviceController
from blueheeler.widgets.common.labeled_entry_widget import LabeledEntryWidget
from blueheeler.widgets.write_dialog import WriteDialog

from ..models.adapters.blecharacteristicadapter import BleCharacteristicAdapter


class DeviceServiceCharacteristicGenericWidget(Gtk.Box):
    UUID_CHAR_WIDTH = 38

    def __init__(self, device_controller: BleDeviceController, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__characteristic: Optional[BleCharacteristicAdapter]= None
        self.__device_controller:BleDeviceController = device_controller
        self.__build_ui()

    def __build_ui(self):
        self.props.spacing = 6
        self.props.orientation = Gtk.Orientation.VERTICAL

        title_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        self.title = Gtk.Label()
        title_box.append(self.title)
        self.append(title_box)

        entries_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        self.append(entries_box)

        self.uuid_widget = LabeledEntryWidget(title=_("UUID"))
        self.uuid_widget.entry.set_width_chars(self.UUID_CHAR_WIDTH)
        entries_box.append(self.uuid_widget)

        self.handle_widget = LabeledEntryWidget(title=_("Handle"))
        entries_box.append(self.handle_widget)

        control_box, self.properties_box = (
            self.__create_characteristic_properties_controls()
        )
        self.append(control_box)

    ################################################################################################
    # Properties
    ################################################################################################
    @GObject.Property(type=BleCharacteristicAdapter)
    def characteristic(self) -> BleCharacteristicAdapter | None:
        return self.__characteristic

    @characteristic.setter  # type: ignore[no-redef]
    def characteristic(self, characteristic: BleCharacteristicAdapter):
        self.__characteristic = characteristic
        self.title.props.label = "{}: {}".format(
            _("Characteristic"), self.__characteristic.description
        )
        self.uuid_widget.entry.props.text = self.__characteristic.uuid
        self.handle_widget.entry.props.text = str(self.__characteristic.handle)

        child = self.properties_box.get_child_at_index(0)
        while child:
            self.properties_box.remove(child)
            child = self.properties_box.get_child_at_index(0)

        for property in self.__characteristic.properties:
            if property == "read":
                property_button = Gtk.ToggleButton(label=_("Read"))
                self.properties_box.insert(property_button, -1)
                property_button.connect("clicked", self.__on_read_button_clicked)
            if property == "notify":
                property_button = Gtk.ToggleButton(label=_("Notify"))
                self.properties_box.insert(property_button, -1)
                property_button.connect("clicked", self.__on_notify_button_clicked)
            if property == "write":
                property_button = Gtk.ToggleButton(label=_("Write"))
                self.properties_box.insert(property_button, -1)
                property_button.connect("clicked", self.__on_write_button_clicked)

    def __on_read_button_clicked(self, sender):
        def on_task_active_changed(task, property_spec):
            sender.set_active(task.is_active)
            sender.set_label(_("Reading...")) if task.is_active else sender.set_label(_("Read"))

        if sender.get_active():
            sender.set_label(_("Reading..."))
            if self.characteristic:
                task = self.__device_controller.read_characteristic(self.characteristic)
                task.connect("notify::is-active", on_task_active_changed)

    def __on_notify_button_clicked(self, sender):
        def on_task_active_changed(task, property_spec):
            sender.set_active(task.is_active)
            sender.set_label(_("Reading notified...")) if task.is_active else sender.set_label(_("Notify"))

        if self.characteristic is None:
            sender.set_active(False)
            return

        if sender.get_active():
            task = self.__device_controller.start_notify_read(self.characteristic)
            task.connect("notify::is-active", on_task_active_changed)
        else:
            self.__device_controller.stop_notify_read(self.characteristic)

    def __on_write_button_clicked(self, sender):
        # TODO PTAR Connect to wait handler as well
        if self.characteristic is not None:
            dialog = WriteDialog(self.get_root(), self.__device_controller, self.characteristic)
            dialog.present()

    def __create_characteristic_properties_controls(self):
        control_box = Gtk.Box(spacing=6)
        control_box.props.margin_start = 12
        control_box.props.margin_top = 6
        control_box.props.margin_bottom = 6
        title_label = Gtk.Label(label=_("Properties:"))
        properties_box = Gtk.FlowBox(orientation=Gtk.Orientation.HORIZONTAL)
        properties_box.props.margin_start = 12
        properties_box.props.margin_top = 6
        properties_box.props.margin_bottom = 6
        properties_box.set_hexpand(True)
        control_box.append(title_label)
        control_box.append(properties_box)

        return control_box, properties_box
