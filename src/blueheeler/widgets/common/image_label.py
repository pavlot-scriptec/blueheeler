import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class ImageLabel(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orientation = Gtk.Orientation.HORIZONTAL
        self.props.spacing = 6
        self.image = Gtk.Image()
        self.label = Gtk.Label()
        self.append(self.image)
        self.append(self.label)
