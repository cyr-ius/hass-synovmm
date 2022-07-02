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

from .const import DOMAIN, PLATFORMS, SET
from .common import async_get_setting_vm, async_get_stats

_LOGGER = logging.getLogger(__name__)

VMCONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): str,
        vol.Required("name"): str,
        vol.Optional("desc"): str,
        vol.Optional("iso_images"): str,
        vol.Optional("guest_privilege"): str,
        vol.Optional("autorun"): int,
        vol.Optional("boot_from"): str,
        vol.Optional("usbs"): str,
        vol.Optional("use_ovmf"): bool,
        vol.Optional("usb_version"): int,
        vol.Optional("old_use_ovmf"): bool,
        vol.Optional("vnics_add"): str,
        vol.Optional("vnics_del"): str,
        vol.Optional("vnics_edit"): str,
        vol.Optional("increaseAllocatedSize"): int,
        vol.Optional("order_changed"): bool,
        vol.Optional("vdisks_add"): str,
        vol.Optional("vdisks_del"): str,
        vol.Optional("vdisks_edit"): str,
        vol.Optional("cpu_weight"): int,
        vol.Optional("cpu_pin_num"): int,
        vol.Optional("vdisk_num"): int,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Syno component."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = SynologyVMMDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    if coordinator.data is None:
        return False

    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    async def async_set_vm(call) -> None:
        entity_registry = await er.async_get_registry(hass)
        entity = entity_registry.async_get(call.data["entity_id"])
        json_params = call.data.copy()
        json_params.pop("entity_id")
        if json_params.get("usbs"):
            json_params["usbs"] = json_params["usbs"].split(",")
        if json_params.get("iso_images"):
            json_params["iso_images"] = json_params["iso_images"].split(",")
        SET.update({"guest_id": entity.unique_id})
        SET.update(json_params)
        params = {"version": 2, "compound": json.dumps([SET])}
        try:
            _LOGGER.debug(f"Service Request: {params}")
            response = await hass.async_add_executor_job(
                coordinator.api.post, "SYNO.Entry.Request", "request", params
            )
            _LOGGER.debug(f"Service Response: {response}")
            if response.get("data", {}).get("has_fail", True):
                raise Exception(response["data"].get("result"))
        except Exception as error:
            raise Exception(error)
        else:
            await coordinator.async_request_refresh()

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
        configurations = {}
        try:
            await self.hass.async_add_executor_job(self.api.information.update)
            vms = await self.hass.async_add_executor_job(
                self.api.post, "SYNO.Virtualization.API.Guest", "list"
            )
            for vm in vms.get("data", {}).get("guests", []):
                gid = vm["guest_id"]
                settings = await async_get_setting_vm(self.hass, self.api, gid)
                stats = await async_get_stats(self.hass, self.api, gid)
                settings["stats"] = stats
                configurations.update({gid: settings})

        except Exception as error:
            raise UpdateFailed(error) from error

        return configurations
