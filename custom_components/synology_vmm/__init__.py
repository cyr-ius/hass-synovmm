"""The Syno component."""
from __future__ import annotations

from datetime import timedelta
import json
import logging

from synology_dsm import SynologyDSM
from synology_dsm.exceptions import SynologyDSMException
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ENTITY_ID,
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SSL,
    CONF_TIMEOUT,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .common import async_get_setting_vm, async_get_stats
from .const import (
    CONF_AUTORUN,
    CONF_BOOT,
    CONF_CPU_PNUM,
    CONF_CPU_WEIGHT,
    CONF_DESC,
    CONF_INC_SIZE,
    CONF_ISO,
    CONF_OLD_OVMF,
    CONF_ORDER,
    CONF_PRIVILEGES,
    CONF_USB_VERSION,
    CONF_USBS,
    CONF_USE_OVMF,
    CONF_VDISK_NUM,
    CONF_VDISKS_ADD,
    CONF_VDISKS_DEL,
    CONF_VDISKS_EDIT,
    CONF_VNICS_ADD,
    CONF_VNICS_DEL,
    CONF_VNICS_EDIT,
    DOMAIN,
    GUEST_ID,
    PLATFORMS,
    SERVICE_SET_VM,
    SET,
)

VMCONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): str,
        vol.Required(CONF_NAME): str,
        vol.Optional(CONF_DESC): str,
        vol.Optional(CONF_ISO): str,
        vol.Optional(CONF_PRIVILEGES): str,
        vol.Optional(CONF_AUTORUN): int,
        vol.Optional(CONF_BOOT): str,
        vol.Optional(CONF_USBS): str,
        vol.Optional(CONF_USE_OVMF): bool,
        vol.Optional(CONF_USB_VERSION): int,
        vol.Optional(CONF_OLD_OVMF): bool,
        vol.Optional(CONF_VNICS_ADD): str,
        vol.Optional(CONF_VNICS_DEL): str,
        vol.Optional(CONF_VNICS_EDIT): str,
        vol.Optional(CONF_INC_SIZE): int,
        vol.Optional(CONF_ORDER): bool,
        vol.Optional(CONF_VDISKS_ADD): str,
        vol.Optional(CONF_VDISKS_DEL): str,
        vol.Optional(CONF_VDISKS_EDIT): str,
        vol.Optional(CONF_CPU_WEIGHT): int,
        vol.Optional(CONF_CPU_PNUM): int,
        vol.Optional(CONF_VDISK_NUM): int,
    }
)

SCAN_INTERVAL = 60
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Syno component."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = SynologyVMMDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def async_set_vm(call) -> None:
        entity_registry = await er.async_get_registry(hass)
        entity = entity_registry.async_get(call.data[CONF_ENTITY_ID])
        json_params = call.data.copy()
        json_params.pop(CONF_ENTITY_ID)
        if json_params.get(CONF_USBS):
            json_params[CONF_USBS] = json_params[CONF_USBS].split(",")
        if json_params.get(CONF_ISO):
            json_params[CONF_ISO] = json_params[CONF_ISO].split(",")
        SET.update({GUEST_ID: entity.unique_id})
        SET.update(json_params)
        params = {"version": 2, "compound": json.dumps([SET])}
        try:
            _LOGGER.debug(f"Service Request: {params}")
            response = await coordinator.api.post(
                "SYNO.Entry.Request", "request", params
            )
            _LOGGER.debug(f"Service Response: {response}")
            if response.get("data", {}).get("has_fail", True):
                raise Exception(response["data"].get("result"))
        except SynologyDSMException as error:
            raise Exception(error)
        else:
            await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN, SERVICE_SET_VM, async_set_vm, schema=VMCONFIG_SCHEMA
    )

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
        """Class to manage fetching data API."""
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=SCAN_INTERVAL)
        )
        self.api = SynologyDSM(
            async_create_clientsession(hass),
            config_entry.data[CONF_IP_ADDRESS],
            config_entry.data[CONF_PORT],
            config_entry.data[CONF_USERNAME],
            config_entry.data[CONF_PASSWORD],
            use_https=config_entry.data[CONF_SSL],
            timeout=config_entry.data[CONF_TIMEOUT],
            device_token=None,
            debugmode=False,
        )

    async def _async_update_data(self) -> dict:
        """Update data."""
        configurations = {}
        try:
            await self.api.information.update()
            vms = await self.api.post("SYNO.Virtualization.API.Guest", "list")
            for vm in vms.get("data", {}).get("guests", []):
                gid = vm[GUEST_ID]
                settings = await async_get_setting_vm(self.hass, self.api, gid)
                stats = await async_get_stats(self.hass, self.api, gid)
                settings["stats"] = stats
                configurations.update({gid: settings})

        except SynologyDSMException as error:
            raise UpdateFailed(error) from error

        return configurations
