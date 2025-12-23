from gi.repository import Gtk

from blueheeler.models.adapters.bledevicecontroller import BleDeviceController
from blueheeler.widgets.device_services_widget import DeviceServicesWidget


class DevicePageFactory:

    @classmethod
    def create_and_attach_to_notebook(
        cls,
        notebook: Gtk.Notebook,
        device_page_indexes: dict[str, int],
        device_controller: BleDeviceController,
    ):
        device_page_indexes[device_controller.device_adapter.address] = (
            notebook.get_n_pages()
        )
        page, page_title = cls.__create(
            notebook, device_page_indexes, device_controller
        )
        notebook.append_page(page, page_title)

    @classmethod
    def __create(
        cls,
        notebook: Gtk.Notebook,
        device_page_indexes: dict[str, int],
        device_controller: BleDeviceController,
    ) -> tuple[Gtk.Widget, Gtk.Widget]:
        page = cls.__build_page(device_controller)
        page_title = cls.__build_title(
            notebook, device_page_indexes, page, device_controller
        )
        return (page, page_title)

    @classmethod
    def __build_title(
        cls,
        notebook: Gtk.Notebook,
        device_page_indexes: dict[str, int],
        page: Gtk.Widget,
        device_controller: BleDeviceController,
    ) -> Gtk.Widget:
        page_title_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        page_title = Gtk.Label(
            label="{} {}".format(
                device_controller.device_adapter.address,
                device_controller.device_adapter.name,
            )
        )
        page_title_box.append(page_title)
        close_button = Gtk.Button(icon_name="window-close-symbolic")
        close_button.add_css_class("flat")
        close_button.connect(
            "clicked",
            lambda b: cls.__close_page(
                notebook, device_page_indexes, page, device_controller
            ),
        )
        page_title_box.append(close_button)
        return page_title_box

    @classmethod
    def __build_page(self, device_controller: BleDeviceController) -> Gtk.Widget:
        return DeviceServicesWidget(device_controller)

    @classmethod
    def __close_page(
        cls,
        notebook: Gtk.Notebook,
        device_page_indexes: dict[str, int],
        page: Gtk.Widget,
        device_controller: BleDeviceController,
    ):
        del device_page_indexes[device_controller.device_adapter.address]
        page_num = notebook.page_num(page)
        if page_num != -1:
            notebook.remove_page(page_num)
        device_controller.release()
