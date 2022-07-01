def list_vm(api):
    """Return list vm."""
    return api.post("SYNO.Virtualization.API.Guest", "list")


async def async_get_setting(hass, api, guest_id):
    """Return list vm."""
    params = {
        "version": 2,
        "compound": '[{"api":"SYNO.Virtualization.Guest","method":"get_setting","version":1,"guest_id":"'
        + guest_id
        + '"},{"api":"SYNO.Virtualization.Guest.Image","method":"list","version":2},{"api":"SYNO.Virtualization.Guest","method":"list_resource","version":1},{"api":"SYNO.Virtualization.Guest","method":"usb_list","version":1,"guest_id":"'
        + guest_id
        + '"},{"api":"SYNO.Virtualization.Host","method":"list","version":2,"show_realtime_data":false},{"api":"SYNO.Virtualization.Repo","method":"list","version":2}]',
    }
    rslt = await hass.async_add_executor_job(api_post, api, params)
    return rslt.get("data", {}).get("result", [])


async def async_usb_list(hass, api, guest_id):
    """Return list vm."""
    params = {
        "version": 2,
        "compound": '[{"api":"SYNO.Virtualization.Guest","method":"usb_list","version":1,"guest_id":"'
        + guest_id
        + '"}]',
    }
    rslt = await hass.async_add_executor_job(api_post, api, params)
    return rslt.get("data", {}).get("result", [])


def api_post(api, params):
    """Call api function."""
    return api.post("SYNO.Entry.Request", "request", params=params)
