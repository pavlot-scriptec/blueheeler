import gi

gi.require_version("Gtk", "4.0")
from gettext import gettext

from gi.repository import GObject, Gtk

_ = gettext

from typing import Optional

from blueheeler.widgets.common.labeled_entry_widget import LabeledEntryWidget

from ..models.adapters.bledevicecontroller import BleDeviceController
from ..models.adapters.bleserviceadapter import BleServiceAdapter
from .device_service_characteristics_widget import DeviceServiceCharacteristicsWidget


class GenericServicePage(Gtk.Box):
    UUID_CHAR_WIDTH = 38

    def __init__(self, device_controller: BleDeviceController, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__service: Optional[BleServiceAdapter] = None
        self.__device_controller: BleDeviceController = device_controller
        self.__build_ui()

    def __build_ui(self):
        self.props.spacing = 6
        self.props.orientation = Gtk.Orientation.VERTICAL

        entries_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        self.append(entries_box)

        self.uuid_widget = LabeledEntryWidget(title=_("UUID"))
        self.uuid_widget.entry.set_width_chars(self.UUID_CHAR_WIDTH)
        entries_box.append(self.uuid_widget)

        self.handle_widget = LabeledEntryWidget(title=_("Handle"))
        entries_box.append(self.handle_widget)

        self.characteristics_widget = DeviceServiceCharacteristicsWidget(
            self.__device_controller
        )
        self.append(self.characteristics_widget)

    ################################################################################################
    # Properties
    ################################################################################################
    @GObject.Property(type=BleServiceAdapter)
    def service(self) -> BleServiceAdapter:
        return self.__service

    @service.setter  # type: ignore[no-redef]
    def service(self, service: BleServiceAdapter):
        self.__service = service
        self.uuid_widget.entry.props.text = self.__service.uuid
        self.uuid_widget.entry.props.width_chars = len(self.__service.uuid)
        self.handle_widget.entry.props.text = str(self.__service.handle)
        self.characteristics_widget.load_characteristics(self.__service)
