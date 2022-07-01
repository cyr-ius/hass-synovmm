"""The Syno component."""
from __future__ import annotations

import json
import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from synology_dsm import SynologyDSM

from .consts import DOMAIN, PLATFORMS
from .common import async_get_setting, list_vm

_LOGGER = logging.getLogger(__name__)

VMCONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): str,
        vol.Required("name"): str,
        vol.Optional("desc", ""): str,
        vol.Optional("iso_images"): str,
        vol.Optional("guest_privilege"): str,
        vol.Required("autorun"): int,
        vol.Required("boot_from", "disk"): str,
        vol.Optional("usbs"): str,
        vol.Required("use_ovmf", True): bool,
        vol.Optional("usb_version", []): int,
        vol.Required("old_use_ovmf", True): bool,
        vol.Optional("vnics_add", []): str,
        vol.Optional("vnics_del", []): str,
        vol.Optional("vnics_edit", []): str,
        vol.Optional("increaseAllocatedSize", 0): int,
        vol.Optional("order_changed", False): bool,
        vol.Optional("vdisks_add", []): str,
        vol.Optional("vdisks_del", []): str,
        vol.Optional("vdisks_edit", []): str,
        vol.Optional("cpu_weight"): int,
        vol.Optional("cpu_pin_num"): int,
        vol.Required("vdisk_num"): int,
    }
)


async def async_setup(hass, config):
    """Load configuration for component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Syno component."""
    coordinator = SynologyVMMDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    if coordinator.data is None:
        return False

    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    async def async_set_vm(call) -> None:

        entity_registry = await er.async_get_registry(hass)
        entity = entity_registry.async_get(call.data["entity_id"])
        params = [
            {
                "api": "SYNO.Virtualization.Guest",
                "method": "set",
                "version": 1,
                "guest_privilege": call.data.get("guest_privilege", []),
                "iso_images": call.data.get("iso_images", ["unmounted", "unmounted"]),
                "autorun": call.data.get("autorun", 2),
                "boot_from": call.data.get("boot_from", "disk"),
                "usbs": call.data.get(
                    "usbs", "unmounted,unmounted,unmounted,unmounted"
                ).split(","),
                "use_ovmf": call.data.get("use_ovmf", True),
                "usb_version": call.data.get("usb_version", 2),
                "old_use_ovmf": call.data.get("old_use_ovmf", True),
                "guest_id": entity.unique_id,
                "vnics_add": call.data.get("vnics_add", []),
                "vnics_del": call.data.get("vnics_del", []),
                "vnics_edit": call.data.get("vnics_edit", []),
                "increaseAllocatedSize": call.data.get("increaseAllocatedSize", 0),
                "order_changed": call.data.get("order_changed", False),
                "vdisks_add": call.data.get("vdisks_add", []),
                "vdisks_del": call.data.get("vdisks_del", []),
                "vdisks_edit": call.data.get("vdisks_edit", []),
                "name": call.data.get("name"),
                "cpu_weight": call.data.get("cpu_weight", 256),
                "desc": call.data.get("desc", ""),
                "cpu_pin_num": call.data.get("cpu_pin_num", 0),
                "vdisk_num": call.data.get("vdisk_num"),
            }
        ]

        def set_entry(api, params):
            params = {"version": 2, "compound": json.dumps(params)}
            _LOGGER.debug(params)
            rslt = api.post("SYNO.Entry.Request", "request", params=params)
            _LOGGER.debug(rslt)
            return rslt

        await hass.async_add_executor_job(set_entry, coordinator.api, params)

    hass.services.async_register(DOMAIN, "set_vm", async_set_vm, schema=VMCONFIG_SCHEMA)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class SynologyVMMDataUpdateCoordinator(DataUpdateCoordinator):
    """Define an object to fetch datas."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry,
    ) -> None:
        """Class to manage fetching Heatzy data API."""
        self.api = SynologyDSM(
            config_entry.data[CONF_IP_ADDRESS],
            config_entry.data[CONF_PORT],
            config_entry.data[CONF_USERNAME],
            config_entry.data[CONF_PASSWORD],
            use_https=False,
            verify_ssl=False,
            timeout=None,
            device_token=None,
            debugmode=False,
        )
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=60)
        )

    async def _async_update_data(self) -> dict:
        try:
            await self.hass.async_add_executor_job(self.api.information.update)
            configurations = await self.async_fetch_data()
            return configurations
        except Exception as error:
            raise UpdateFailed(error) from error

    async def async_fetch_data(self) -> dict:
        """Fetch configuration for all vms."""
        vms = await self.hass.async_add_executor_job(list_vm, self.api)
        configurations = {}
        for vm in vms.get("data", {}).get("guests", []):
            settings = await async_get_setting(self.hass, self.api, vm["guest_id"])
            configuration = {}
            for setting in settings:
                category = f"{setting.get('api')}.{setting.get('method')}"
                configuration.update({category: setting.get("data", {})})
            configurations.update({vm["guest_id"]: configuration})
        return configurations
