"""Helpers functions synology api."""
import json
import logging

from .const import USBS, SETTINGS, ADV_SETTINGS

_LOGGER = logging.getLogger(__name__)


async def async_get_setting_vm(hass, api, guest_id):
    """Return list vm."""
    infos = {}
    SETTINGS.update({"guest_id": guest_id})
    ADV_SETTINGS.update({"guest_id": guest_id})
    params = {"version": 2, "compound": json.dumps([SETTINGS, USBS, ADV_SETTINGS])}
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
