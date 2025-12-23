import logging

import pytest

from automation.app_runner import AppRunner
from automation.wait import wait_for_condition
from blueheeler.application import Application
from blueheeler.models.adapters.bledeviceadapter import BleDeviceAdapter
from blueheeler.models.deviceliststore import DeviceListStore


@pytest.mark.asyncio
@pytest.mark.config
class TestScanForDevices:
    async def test_device_lookup_and_selection(self, config):
        def find_device_in_store(store: DeviceListStore, address: str):
            for i in range(store.get_n_items()):
                device = store.get_item(i)
                assert device is not None
                assert isinstance(device, BleDeviceAdapter)
                logging.info(f"TODO PTAR Remove it: device addr {device.address} looking for: {address}")
                if device.address == address:
                    return i, device
            return None        
        app: Application = Application()
        async with AppRunner(app) as runner:
            device_address = config["test_device_addresses"][0]
            assert device_address
            await wait_for_condition(
                lambda: app.main_window and app.main_window.get_visible(), timeout=1
            )
            
            # Click scan button
            runner.idle_add(app.main_window.scan_button.emit, "clicked")
            await wait_for_condition(
                lambda: app.main_window.scan_for_devices_dialog
                and app.main_window.scan_for_devices_dialog.get_visible(),
                timeout=1,
            )

            await wait_for_condition(lambda: find_device_in_store(app.device_repository.devices, device_address), timeout=10)
            index, device = find_device_in_store(app.device_repository.devices, device_address)
            factory = app.main_window.scan_for_devices_dialog.list_liew_devices.get_factory()
            assert factory
            runner.idle_add(factory.emit, "signal_device_selected", device)
            await wait_for_condition(lambda: app.main_window.devices_notebook.get_n_pages()==1, timeout=10)

            # Click scan button
            runner.idle_add(app.main_window.scan_button.emit, "clicked")
            await wait_for_condition(
                lambda: app.main_window.scan_for_devices_dialog
                and app.main_window.scan_for_devices_dialog.get_visible(),
                timeout=1,
            )

            await wait_for_condition(lambda: find_device_in_store(app.device_repository.devices, device_address), timeout=10)
            index, device = find_device_in_store(app.device_repository.devices, device_address)
            factory = app.main_window.scan_for_devices_dialog.list_liew_devices.get_factory()
            assert factory
            runner.idle_add(factory.emit, "signal_device_selected", device)
            await wait_for_condition(
                lambda: not app.main_window.scan_for_devices_dialog.get_visible(),
                timeout=1,
            )

            # Click scan button
            runner.idle_add(app.main_window.scan_button.emit, "clicked")
            await wait_for_condition(
                lambda: app.main_window.scan_for_devices_dialog
                and app.main_window.scan_for_devices_dialog.get_visible(),
                timeout=1,
            )

            await wait_for_condition(lambda: find_device_in_store(app.device_repository.devices, device_address), timeout=10)
            index, device = find_device_in_store(app.device_repository.devices, device_address)
            factory = app.main_window.scan_for_devices_dialog.list_liew_devices.get_factory()
            assert factory
            runner.idle_add(factory.emit, "signal_device_selected", device)
            await wait_for_condition(
                lambda: not app.main_window.scan_for_devices_dialog.get_visible(),
                timeout=1,
            )

            await wait_for_condition(lambda: app.main_window.devices_notebook.get_n_pages()==1, timeout=10)
