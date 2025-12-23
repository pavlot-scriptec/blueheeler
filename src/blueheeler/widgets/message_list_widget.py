import gi

gi.require_version("Gtk", "4.0")
from gettext import gettext
from typing import Any

from gi.repository import Gio, GLib, Gtk

_ = gettext

class MessageColumnFactory(Gtk.SignalListItemFactory):
    def __init__(self, column_path:str, **kwargs):
        super().__init__(**kwargs)
        self.__column_path:str = column_path
        self.connect("setup", self.__on_setup)
        self.connect("bind", self.__on_bind)

    def __on_setup(self, factory, list_item):
        label = Gtk.Label(xalign=0)
        list_item.set_child(label)

    def __on_bind(self, factory, list_item):
        label: Gtk.Label = list_item.get_child()
        item = list_item.get_item()
        attribute = self.__get_object_from_path(item, self.__column_path)
        if attribute is None:
            label.set_text("")
        elif isinstance(attribute, GLib.DateTime):
            label.set_text(str(attribute.format_iso8601()))
        else:
            label.set_text(str(attribute))

    def __get_object_from_path(self, item:Any, path:str):
        path_parts = path.split(".")
        if len(path_parts)==0:
            return None
        
        attr = item
        while path_parts and attr is not None:
            path_part = path_parts.pop(0)
            attr = getattr(attr, path_part, None)
        return attr

class MessageListWidget(Gtk.Box):
    def __init__(self, message_store:Gio.ListStore, **kwargs):
        super().__init__(**kwargs)
        self.__columns:list[Gtk.ColumnViewColumn] = []

        self.read_data_column_view = Gtk.ColumnView()
        self.__action_group = Gio.SimpleActionGroup()     
        self.insert_action_group("column", self.__action_group)   
        self.__header_menu = Gio.Menu()

        factory = MessageColumnFactory("timestamp")
        self.__create_resizable_column(self.read_data_column_view, factory, _("Timestamp"), 260)

        factory = MessageColumnFactory("characteristic.service.device.address")
        self.__create_resizable_column(self.read_data_column_view, factory, _("device.address"), 150)

        factory = MessageColumnFactory("characteristic.service.device.name")
        self.__create_resizable_column(self.read_data_column_view, factory, _("device.name"), 150)

        factory = MessageColumnFactory("characteristic.service.uuid")
        self.__create_resizable_column(self.read_data_column_view, factory, _("service.uuid"), 280)

        factory = MessageColumnFactory("characteristic.service.description")
        self.__create_resizable_column(self.read_data_column_view, factory, _("service.description"), 260)

        factory = MessageColumnFactory("characteristic.description")
        self.__create_resizable_column(self.read_data_column_view, factory, _("characteristic.description"), 260)

        factory = MessageColumnFactory("characteristic.uuid")
        self.__create_resizable_column(self.read_data_column_view, factory, _("characteristic.uuid"), 280)

        factory = MessageColumnFactory("descriptor.description")
        self.__create_resizable_column(self.read_data_column_view, factory, _("descriptor.description"), 260)

        factory = MessageColumnFactory("descriptor.uuid")
        self.__create_resizable_column(self.read_data_column_view, factory, _("descriptor.uuid"), 280)

        factory = MessageColumnFactory("size")
        self.__create_resizable_column(self.read_data_column_view, factory, _("Size"), 40)

        factory = MessageColumnFactory("is_incoming")
        self.__create_resizable_column(self.read_data_column_view, factory, _("Incoming"), 40)

        self.read_data_column_view.add_css_class("packets-list")
        self.read_data_column_view.props.hexpand = True
        self.read_data_column_view.props.vexpand = True

        self.__scrolled_window = Gtk.ScrolledWindow()
        self.__scrolled_window.set_propagate_natural_width(True)
        self.__scrolled_window.set_propagate_natural_height(True)
        self.__scrolled_window.add_css_class("packets-list")
        self.__scrolled_window.set_child(self.read_data_column_view)
        self.__scrolled_window.props.vexpand = True

        self.selection = Gtk.SingleSelection(model=message_store)

        def select_last_row(store, position, removed, added):
            n = store.get_n_items()
            if n == 0:
                return
            self.selection.select_item(n - 1, True)
        message_store.connect("items-changed", select_last_row)

        self.read_data_column_view.set_model(self.selection)
        self.append(self.__scrolled_window)        

    def __create_resizable_column(self, column_view, factory, title:str, width:int):
        col_idx = len(self.__columns)
        column = Gtk.ColumnViewColumn.new(title, factory)
        column.set_fixed_width(width)
        column.set_resizable(True)
        column_view.append_column(column)
        self.__columns.append(column)

        action_id = f"toggle_visibility_{col_idx}"
        action = Gio.SimpleAction.new_stateful(action_id, None, GLib.Variant.new_boolean(True))
        action.connect("change-state", self.__on_column_toggled, column)
        self.__action_group.add_action(action)
        self.__header_menu.append(title, f"column.{action_id}")
        column.set_header_menu(self.__header_menu)

    def __on_column_toggled(self, action, state, column):
        new_state = not action.get_state().get_boolean()
        action.set_state(GLib.Variant.new_boolean(new_state))
        column.set_visible(new_state)