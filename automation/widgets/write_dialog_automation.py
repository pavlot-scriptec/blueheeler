import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib


class WriteDialogAutomation:
    """
    Automation wrapper for an WriteDialog widget.
    """

    def __init__(self, dialog):
        self._dialog = dialog

    def enter_text(self, text: str):
        buffer = self._dialog._WriteDialog__buffer
        buffer.set_text(text)

    def click_write(self):
        button = self._dialog._WriteDialog__write_button
        button.emit("clicked")

    def get_written_bytes_from_mock(self, mock_method):
        args, _ = mock_method.call_args
        written_bytes = args[1]
        assert isinstance(written_bytes, GLib.Bytes)
        return written_bytes.get_data()

    def destroy(self):
        self._dialog.destroy()