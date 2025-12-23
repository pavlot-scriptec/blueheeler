import gi

gi.require_version("Gtk", "4.0")

import asyncio
from typing import Union

from gi.repository import GLib, Gtk

from automation.wait import wait_for_condition


class AppRunner:
    def __init__(self, app: Gtk.Application):
        self.__app: Gtk.Application = app
        self.__task: Union[asyncio.Task | None] = None
        self.__exit_condition: asyncio.Event = asyncio.Event()
        self.__lock: asyncio.Lock = asyncio.Lock()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop()
        await wait_for_condition(lambda: self.__task is None, timeout=5)

    async def __run_app(self):
        self.__app.register(None)
        self.__app.activate()

        try:
            while not self.__exit_condition.is_set():
                while GLib.MainContext.default().iteration(False):
                    pass
                await asyncio.sleep(0.01)
        finally:
            self.__app.quit()
            self.__task = None

    async def start(self):
        async with self.__lock:
            if self.__task is None:
                self.__task = asyncio.create_task(self.__run_app())

    async def stop(self):
        async with self.__lock:
            self.__exit_condition.set()

    def idle_add(self, function, *args):
        GLib.idle_add(function, *args)
