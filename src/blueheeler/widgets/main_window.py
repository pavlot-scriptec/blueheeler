from gettext import gettext

from gi.repository import Adw, Gdk, Gio, GObject, Gtk

from blueheeler.widgets.device_page_factory import DevicePageFactory

_ = gettext

from importlib.metadata import metadata
from typing import Optional

from blueheeler.models.adapters.bledeviceadapter import BleDeviceAdapter
from blueheeler.models.adapters.bledevicecontroller import BleDeviceController
from blueheeler.models.data_collector import DataCollector
from blueheeler.models.device_repository import DeviceRepository
from blueheeler.widgets.message_list_widget import MessageListWidget
from blueheeler.widgets.scan_for_devices_dialog import ScanForDevicesDialog


class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, device_repository: DeviceRepository, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title(_("GTK4 bluetooth analyzer"))
        self.set_icon_name("blue-heeler-logo")

        self.__device_repository: DeviceRepository = device_repository
        self.__data_collector: DataCollector = DataCollector()

        self.__initialize_header()

        self.scan_for_devices_dialog: Optional[ScanForDevicesDialog] = None

        self.__box_main_layout = Gtk.Box()
        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        self.__box_main_layout.append(paned)
        self.set_child(self.__box_main_layout)

        self.__devices_frame = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.__devices_frame.props.hexpand = True

        self.__devices_notebook = Gtk.Notebook()
        self.__devices_notebook.props.scrollable = True
        self.__devices_notebook.props.hexpand = True
        self.__devices_frame.append(self.__devices_notebook)
        self.__device_page_indexes: dict = {}

        self.packets_frame, self.__decoding_buffer = self.__build_packets_frame()

        paned.set_start_child(self.__devices_frame)
        paned.set_shrink_start_child(False)
        paned.set_resize_start_child(False)
        paned.set_end_child(self.packets_frame)

        self.__center_window()

    def __center_window(self):
        self.present()
        display = Gdk.Display.get_default()
        if not display:
            raise RuntimeError("Unable to get default display")

        surface = self.get_surface()
        if not surface:
            raise RuntimeError("Unable to get surface")

        monitor = display.get_monitor_at_surface(surface)
        if monitor:
            geometry = monitor.get_geometry()
            width = int(geometry.width * 0.9)
            height = int(geometry.height * 0.8)
            self.set_default_size(width, height)

    def __initialize_header(self):
        self.__header = Gtk.HeaderBar()
        self.set_titlebar(self.__header)
        self.scan_button = Gtk.Button(label=_("Scan"))
        self.scan_button.connect("clicked", self.__on_scan_button_clicked)
        self.__header.pack_start(self.scan_button)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.__on_about)
        self.add_action(about_action)

        menu = Gio.Menu()
        menu.append("About", "win.about")

        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_menu_model(menu)
        menu_button.set_tooltip_text("Menu")
        self.__header.pack_end(menu_button)

    def __on_scan_button_clicked(self, button):
        self.scan_for_devices_dialog = ScanForDevicesDialog(
            self, self.__device_repository
        )
        self.scan_for_devices_dialog.connect(
            "signal_device_selected", self.__on_device_selected
        )
        self.scan_for_devices_dialog.present()

    def __on_device_selected(self, dialog, device_adapter: BleDeviceAdapter):
        device_controller, is_created = (
            self.__device_repository.get_or_create_device_controller(device_adapter)
        )
        if is_created:
            device_controller.load_services_task.start()
            device_controller.connect(
                "signal_characteristic_data_received",
                lambda sender, characteristic, data: self.__data_collector.collect_characteristic_data(
                    characteristic, True, data
                ),
            )
            device_controller.connect(
                "signal_descriptor_data_received",
                lambda sender, descriptor, data: self.__data_collector.collect_characteristic_data(
                    descriptor, True, data
                ),
            )
            device_controller.connect(
                "signal_characteristic_data_sent",
                lambda sender, characteristic, data: self.__data_collector.collect_characteristic_data(
                    characteristic, False, data
                ),
            )
            device_controller.connect(
                "signal_descriptor_data_sent",
                lambda sender, descriptor, data: self.__data_collector.collect_characteristic_data(
                    descriptor, False, data
                ),
            )
        self.__build_device_page(self.__devices_notebook, device_controller)

    def __build_device_page(self, notebook, device_controller: BleDeviceController):
        if device_controller.device_adapter.address in self.__device_page_indexes:
            notebook.set_current_page(
                self.__device_page_indexes[device_controller.device_adapter.address]
            )
            return

        DevicePageFactory.create_and_attach_to_notebook(notebook, self.__device_page_indexes, device_controller)

    def __build_packets_frame(self):
        packets_frame = Gtk.Box(spacing=6)
        packets_frame.props.hexpand = True
        packets_frame.props.vexpand = True
        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)

        # Message list-------------------------------------------------------------------------------
        message_list_widget = MessageListWidget(self.__data_collector.data_store)
        message_list_widget.selection.connect("notify::selected-item", self.__on_message_selection_changed)
        paned.set_start_child(message_list_widget)

        # TODO PTAR This is place where decoders should be initialized
        # Text view ---------------------------------------------------------------------------------
        scrolled_window = Gtk.ScrolledWindow()
        buffer = Gtk.TextBuffer()
        text_view = Gtk.TextView.new_with_buffer(buffer)
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
        paned.set_end_child(scrolled_window)

        packets_frame.append(paned)

        return packets_frame, buffer

    def __on_message_selection_changed(self, model, position):
        def to_ascii_hex(data: bytes) -> str:
            return "".join(chr(b) if 32 <= b < 127 else f"\\x{b:02x}" for b in data)

        packet = model.get_selected_item()
        self.__decoding_buffer.set_text(to_ascii_hex(packet.data.get_data()))


    def __on_about(self, action, param):
        pkg_name = "blueheeler"
        meta = metadata(pkg_name)

        about = Adw.AboutDialog(
            application_name=meta["Name"],
            application_icon="blue-heeler-logo",
            version=meta["Version"],
            license_type=Gtk.License.MIT_X11,
        )
        about.present()

    ################################################################################################
    # Properties
    ################################################################################################
    @GObject.Property(type=Gtk.Notebook)
    def devices_notebook(self):
        return self.__devices_notebook

    ################################################################################################
    # Signals
    ################################################################################################
