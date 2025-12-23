import gi

gi.require_version("Gtk", "4.0")
from gettext import gettext
from importlib import resources

from gi.repository import Gdk, Gio, Gtk

_ = gettext


class StyleManager:

    @classmethod
    def initialize(cls):
        cls.load_resources()
        cls.set_default_style()

    @classmethod
    def set_default_style(cls):
        with resources.as_file(
            resources.files("blueheeler").joinpath("assets/blue-heeler.css")
        ) as css_path:
            provider = Gtk.CssProvider()
            provider.load_from_path(str(css_path))

            display = Gdk.Display.get_default()
            if display:
                Gtk.StyleContext.add_provider_for_display(
                    display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

    @classmethod
    def load_resources(cls):
        with resources.as_file(
            resources.files("blueheeler").joinpath("resources.gresource")
        ) as resource_path:
            resource = Gio.Resource.load(str(resource_path))
            Gio.resources_register(resource)

            display = Gdk.Display.get_default()
            if not display:
                raise RuntimeError("Unable to get default display")

            icon_theme = Gtk.IconTheme.get_for_display(display)
            icon_theme.add_resource_path(
                "/pl/scriptec/blue-heeler/assets/icons/hicolor"
            )
