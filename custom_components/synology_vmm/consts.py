"""Constants for the Syno component."""
DOMAIN = "synology_vmm"
USB_DEVICE = "usb_device"
GUEST_ID = "guest_id"
PLATFORMS = ["switch"]
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
