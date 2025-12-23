import gi

from blueheeler.widgets.common.labeled_entry_widget import LabeledEntryWidget

gi.require_version("Gtk", "4.0")
from gettext import gettext

from gi.repository import GObject, Gtk

_ = gettext


from typing import Optional

from blueheeler.models.adapters.bledevicecontroller import BleDeviceController
from blueheeler.widgets.write_dialog import WriteDialog

from ..models.adapters.blecharacteristicdescriptoradapter import (
    BleCharacteristicDescriptorAdapter,
)


class DeviceServiceCharacteristicDescriptorGenericWidget(Gtk.Box):
    UUID_CHAR_WIDTH = 38

    def __init__(self, device_controller: BleDeviceController, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__descriptor: Optional[BleCharacteristicDescriptorAdapter] = None
        self.__device_controller: BleDeviceController = device_controller
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

        self.uuid_widget = LabeledEntryWidget(_("UUID"))
        self.uuid_widget.entry.set_width_chars(self.UUID_CHAR_WIDTH)
        entries_box.append(self.uuid_widget)

        self.handle_widget = LabeledEntryWidget(_("Handle"))
        entries_box.append(self.handle_widget)

        control_box, self.properties_box = (
            self.__create_action_controls()
        )
        self.append(control_box)

    ################################################################################################
    # Properties
    ################################################################################################
    @GObject.Property(type=BleCharacteristicDescriptorAdapter)
    def descriptor(self) -> Optional[BleCharacteristicDescriptorAdapter]:
        return self.__descriptor

    @descriptor.setter  # type: ignore[no-redef]
    def descriptor(self, descriptor: BleCharacteristicDescriptorAdapter):
        self.__descriptor = descriptor
        self.title.props.label = "{}: {}".format(
            _("Descriptor"), self.__descriptor.description
        )
        self.uuid_widget.entry.props.text = self.__descriptor.uuid
        self.handle_widget.entry.props.text = str(self.__descriptor.handle)

        child = self.properties_box.get_child_at_index(0)
        while child:
            self.properties_box.remove(child)
            child = self.properties_box.get_child_at_index(0)

        read_button = Gtk.ToggleButton(label=_("Read"))
        self.properties_box.insert(read_button, -1)
        read_button.connect("clicked", self.__on_read_button_clicked)

        write_button = Gtk.Button(label=_("Write"))
        self.properties_box.insert(write_button, -1)
        write_button.connect("clicked", self.__on_write_button_clicked)

    def __on_read_button_clicked(self, sender):
        def on_task_active_changed(task, property_spec):
            sender.set_active(task.is_active)
            (
                sender.set_label(_("Reading..."))
                if task.is_active
                else sender.set_label(_("Read"))
            )

        if sender.get_active():
            sender.set_label(_("Reading..."))
            if self.descriptor:
                task = self.__device_controller.read_descriptor(self.descriptor)
                task.connect("notify::is-active", on_task_active_changed)

    def __on_write_button_clicked(self, sender):
        if self.descriptor is not None:
            dialog = WriteDialog(
                self.get_root(), self.__device_controller, self.descriptor
            )
            dialog.present()

    def __create_action_controls(self):
        control_box = Gtk.Box(spacing=6)
        control_box.props.margin_start = 12
        control_box.props.margin_top = 6
        control_box.props.margin_bottom = 6
        title_label = Gtk.Label(label=_("Actions:"))
        properties_box = Gtk.FlowBox(orientation=Gtk.Orientation.HORIZONTAL)
        properties_box.props.margin_start = 12
        properties_box.props.margin_top = 6
        properties_box.props.margin_bottom = 6
        properties_box.set_hexpand(True)
        control_box.append(title_label)
        control_box.append(properties_box)

        return control_box, properties_box
