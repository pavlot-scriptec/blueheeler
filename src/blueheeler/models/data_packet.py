import gi

gi.require_version("GLib", "2.0")
gi.require_version("GObject", "2.0")
from datetime import datetime
from typing import Optional, Union

from gi.repository import GLib, GObject

from blueheeler.models.adapters.blecharacteristicadapter import BleCharacteristicAdapter
from blueheeler.models.adapters.blecharacteristicdescriptoradapter import (
    BleCharacteristicDescriptorAdapter,
)


class DataPacket(GObject.Object):

    def __init__(
        self,
        characteristic: BleCharacteristicAdapter,
        descriptor: Optional[BleCharacteristicDescriptorAdapter],
        is_incoming: bool = True,
        data: Optional[Union[GLib.Bytes, bytes, bytearray]] = None,
        timestamp: Optional[Union[GLib.DateTime, datetime]] = None,
    ) -> None:
        super().__init__()

        self.__characteristic: BleCharacteristicAdapter = characteristic
        self.__descriptor: Optional[BleCharacteristicDescriptorAdapter] = descriptor
        self.__is_incoming: bool = is_incoming

        # Convert data input
        if data is None:
            data = GLib.Bytes.new(b"")
        elif isinstance(data, (bytes, bytearray)):
            data = GLib.Bytes.new(bytes(data))
        elif not isinstance(data, GLib.Bytes):
            raise TypeError("data must be GLib.Bytes, bytes, bytearray, or None")

        # Convert timestamp input
        if timestamp is None:
            timestamp = GLib.DateTime.new_now_local()
        elif isinstance(timestamp, datetime):
            timestamp = GLib.DateTime.new_from_unix_local(int(timestamp.timestamp()))
        elif not isinstance(timestamp, GLib.DateTime):
            raise TypeError(
                "timestamp must be GLib.DateTime, datetime.datetime, or None"
            )

        assert timestamp
        self.__timestamp: GLib.DateTime = timestamp
        self.__data: GLib.Bytes = data

    ################################################################################################
    # Properties
    ################################################################################################
    @GObject.Property(type=BleCharacteristicAdapter)
    def characteristic(self) -> BleCharacteristicAdapter:
        return self.__characteristic

    @GObject.Property(type=BleCharacteristicDescriptorAdapter)
    def descriptor(self) -> Optional[BleCharacteristicDescriptorAdapter]:
        return self.__descriptor

    @GObject.Property(type=GLib.DateTime)
    def timestamp(self) -> GLib.DateTime:
        return self.__timestamp

    @GObject.Property(type=GLib.Bytes)
    def data(self) -> GLib.Bytes:
        return self.__data

    @GObject.Property(type=int)
    def size(self) -> int:
        return len(self.get_data_as_bytearray())

    @GObject.Property(type=bool, default=True)
    def is_incoming(self) -> bool:
        return self.__is_incoming

    def get_timestamp_as_datetime(self) -> datetime:
        try:
            return datetime.fromtimestamp(self.timestamp.to_unix())
        except AttributeError:
            iso = self.timestamp.format_iso8601()
            return datetime.fromisoformat(iso.replace("Z", "+00:00"))

    def get_data_as_bytearray(self) -> bytearray:
        return bytearray(self.data.get_data())

    def __repr__(self) -> str:
        size = self.size
        try:
            ts_iso = self.timestamp.format_iso8601()
        except Exception:
            ts_iso = "<GLib.DateTime>"
        return f"<DataPacket timestamp={ts_iso} size={size} bytes>"
