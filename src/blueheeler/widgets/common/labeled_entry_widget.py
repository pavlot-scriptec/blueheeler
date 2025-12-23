import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class LabeledEntryWidget(Gtk.Box):
    def __init__(self, title: str, editable: bool = False, **kwargs):
        super().__init__(**kwargs)

        self.props.spacing = 6
        self.props.margin_start = 12
        self.props.margin_top = 6
        self.props.margin_bottom = 6
        self.set_halign(Gtk.Align.START)
        self.label = Gtk.Label(label=title)
        self.label.set_halign(Gtk.Align.START)
        self.entry = Gtk.Entry()
        self.entry.props.editable = editable
        self.entry.set_halign(Gtk.Align.START)
        self.append(self.label)
        self.append(self.entry)
        self.set_hexpand(False)
