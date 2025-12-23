import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


class MockListItem(Gtk.ListItem):
    """A test subclass that returns a given data item."""
    def __init__(self, item):
        super().__init__()
        self._item = item

    def get_item(self):
        return self._item
