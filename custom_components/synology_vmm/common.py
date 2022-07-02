"""Helpers functions synology api."""
import json
import logging

from .const import USBS

_LOGGER = logging.getLogger(__name__)


async def async_get_setting_vm(hass, api, guest_id):
    """Return list vm."""
    infos = {}
    settings = {
        "api": "SYNO.Virtualization.API.Guest",
        "method": "get",
        "version": 1,
        "guest_id": guest_id,
    }
    adv_settings = {
        "api": "SYNO.Virtualization.Guest",
        "method": "get_setting",
        "version": 1,
        "guest_id": guest_id,
    }

    compound = json.dumps([settings, USBS, adv_settings])
    params = {"version": 2, "compound": compound}
    try:
        rslt = await hass.async_add_executor_job(
            api.post, "SYNO.Entry.Request", "request", params
        )
        if rslt.get("data").get("has_fail", True) is False:
            for data in rslt.get("data", {}).get("result", []):
                if usbs := infos.get("usbs"):
                    infos["usb_list"] = usbs
                infos.update(data["data"])
    except Exception as error:
        _LOGGER.error(error)
    return infos


async def async_get_stats(hass, api, guest_id=None):
    """Get statistics virtual machine."""
    stats = []
    try:
        rslt = await hass.async_add_executor_job(
            api.post, "SYNO.Virtualization.Cluster", "get_guest"
        )
        stats = rslt.get("data", {}).get("guests", [])
        if guest_id:
            for stat in stats:
                if stat["id"] == guest_id:
                    return stat
    except Exception as error:
        _LOGGER.error(error)
    return stats
