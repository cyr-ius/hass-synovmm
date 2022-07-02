"""Constants for the Syno component."""
DOMAIN = "synology_vmm"
USB_DEVICE = "usb_device"
GUEST_ID = "guest_id"
PLATFORMS = ["switch", "sensor"]
IMAGES = {
    "api": "SYNO.Virtualization.Guest.Image",
    "method": "list",
    "version": 2,
}
RESSOURCES = {
    "api": "SYNO.Virtualization.Guest",
    "method": "list_resource",
    "version": 1,
}
USBS = {
    "api": "SYNO.Virtualization.Guest",
    "method": "usb_list",
    "version": 1,
}
HOSTS = {
    "api": "SYNO.Virtualization.Host",
    "method": "list",
    "version": 2,
    "show_realtime_data": False,
}
REPOS = {
    "api": "SYNO.Virtualization.Host",
    "method": "list",
    "version": 2,
}
SETTINGS = {
    "api": "SYNO.Virtualization.API.Guest",
    "method": "get",
    "version": 1,
}
ADV_SETTINGS = {
    "api": "SYNO.Virtualization.Guest",
    "method": "get_setting",
    "version": 1,
}
SET = {
    "api": "SYNO.Virtualization.Guest",
    "method": "set",
    "version": 1,
}
