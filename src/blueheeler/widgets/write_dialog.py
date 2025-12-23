import gi

gi.require_version("Gtk", "4.0")
from gettext import gettext

from gi.repository import GLib, Gtk

_ = gettext


from blueheeler.models.adapters.blecharacteristicadapter import BleCharacteristicAdapter
from blueheeler.models.adapters.blecharacteristicdescriptoradapter import (
    BleCharacteristicDescriptorAdapter,
)
from blueheeler.models.adapters.bledevicecontroller import BleDeviceController


class WriteDialog(Gtk.Window):
    def __init__(
        self,
        parent,
        device_controller: BleDeviceController,
        write_object: BleCharacteristicAdapter | BleCharacteristicDescriptorAdapter,
    ):
        super().__init__(title=_("Write"), transient_for=parent, modal=True)
        self.__write_object: (
            BleCharacteristicAdapter | BleCharacteristicDescriptorAdapter
        ) = write_object
        self.__device_controller: BleDeviceController = device_controller

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

        scrolled_window = Gtk.ScrolledWindow()
        self.__buffer = Gtk.TextBuffer()
        text_view = Gtk.TextView.new_with_buffer(self.__buffer)
        text_view.set_monospace(True)
        text_view.set_cursor_visible(True)
        text_view.set_wrap_mode(Gtk.WrapMode.NONE)
        text_view.props.hexpand = True
        text_view.props.vexpand = True

        scrolled_window.set_child(text_view)

        scrolled_window.set_propagate_natural_width(True)
        scrolled_window.set_propagate_natural_height(True)
        scrolled_window.props.hexpand = True
        scrolled_window.props.vexpand = True
        box.append(scrolled_window)

        self.__write_button = Gtk.Button(label=_("Write"))
        box.append(self.__write_button)

        self.set_child(box)

    def __connect_signals(self):
        self.__write_button.connect("clicked", self.__on_write_button_clicked)

    def __on_write_button_clicked(self, sender):
        def ascii_hex_to_bytes(s: str) -> bytearray:
            decoded = s.encode().decode("unicode_escape")
            return bytearray(decoded, "latin1")

        start_iter = self.__buffer.get_start_iter()
        end_iter = self.__buffer.get_end_iter()
        text = self.__buffer.get_text(start_iter, end_iter, True)
        data = ascii_hex_to_bytes(text)
        if isinstance(self.__write_object, BleCharacteristicAdapter):
            self.__device_controller.write_characteristic(
                self.__write_object, GLib.Bytes.new(data)
            )
        if isinstance(self.__write_object, BleCharacteristicDescriptorAdapter):
            self.__device_controller.write_descriptor(
                self.__write_object, GLib.Bytes.new(data)
            )
