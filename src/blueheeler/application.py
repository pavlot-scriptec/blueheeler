import asyncio
import logging
from typing import Optional

import gi

gi.require_version('Gtk', '4.0')
from gi.events import GLibEventLoopPolicy
from gi.repository import GObject, Gtk

from blueheeler.models.device_repository import DeviceRepository

# import logging.config
from blueheeler.widgets.main_window import MainWindow

# BLEAK_GTK_CONFIG = # TODO Implement config

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(relativeCreated)6d %(levelname)s %(threadName)s %(filename)s:%(lineno)d %(message)s",
)
# logging.config.dictConfig(BLEAK_GTK_CONFIG["logging"]) # TODO Logging

from .style_manager import StyleManager


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):

        self.__main_window:Optional[MainWindow] = None
        kwargs["application_id"]="pl.scriptec.blue-heeler"
        super().__init__(*args, **kwargs)
        self.device_repository = DeviceRepository()
        StyleManager.initialize()
    
    
    def do_activate(self):
        self.__main_window = MainWindow(
            device_repository=self.device_repository, application=self
        )
        self.__main_window.present()

    ################################################################################################
    # Properties
    ################################################################################################
    @GObject.Property(type=MainWindow)
    def main_window(self):
        return self.__main_window


def main():
    asyncio.set_event_loop_policy(GLibEventLoopPolicy())
    app = Application()
    app.run(None)


if __name__ == "__main__":
    asyncio.run(main())
