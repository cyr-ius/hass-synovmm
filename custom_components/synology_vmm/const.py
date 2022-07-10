"""Constants for the Syno component."""
CONF_AUTORUN = "autorun"
CONF_BOOT = "boot_from"
CONF_CPU_PNUM = "cpu_pin_num"
CONF_CPU_WEIGHT = "cpu_weight"
CONF_DESC = "desc"
CONF_INC_SIZE = "increaseAllocatedSize"
CONF_ISO = "iso_images"
CONF_OLD_OVMF = "old_use_ovmf"
CONF_ORDER = "order_changed"
CONF_PRIVILEGES = "guest_privilege"
CONF_USB_VERSION = "usb_version"
CONF_USBS = "usbs"
CONF_USE_OVMF = "use_ovmf"
CONF_VDISK_NUM = "vdisk_num"
CONF_VDISKS_ADD = "vdisks_add"
CONF_VDISKS_DEL = "vdisks_del"
CONF_VDISKS_EDIT = "vdisks_edit"
CONF_VNICS_ADD = "vnics_add"
CONF_VNICS_DEL = "vnics_del"
CONF_VNICS_EDIT = "vnics_edit"

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
SERVICE_SET_VM = "set_vm"
SCAN_INTERVAL = 60
