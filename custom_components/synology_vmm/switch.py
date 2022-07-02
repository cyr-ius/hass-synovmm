"""Switch for Synology virtual machine."""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .consts import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    for unique_id in coordinator.data.keys():
        entities.append(VMSensor(coordinator, unique_id))

    async_add_entities(entities)


class VMSensor(CoordinatorEntity, SwitchEntity):
    """Sensor vm infos."""

    entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, unique_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_unique_id = unique_id
        self._attr_name = coordinator.data[unique_id]["guest_name"]

    @property
    def is_on(self):
        """Return status."""
        return self.coordinator.data[self.unique_id]["status"] == "running"

    @property
    def extra_state_attributes(self):
        """Extra attributes."""
        infos = self.coordinator.data[self.unique_id]

        usb_list = []
        for usb in infos.get("usb_list", []):
            if usb["disabled"] is False:
                usb_list.append({usb["usb_id"]: usb["product_name"]})

        attributes = {"usb_list": usb_list, "usb_mounted": infos.get("usbs", [])}
        return attributes

    @property
    def device_info(self):
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=self.name,
            manufacturer=DOMAIN,
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.post,
            "SYNO.Virtualization.API.Guest.Action",
            "poweron",
            {"guest_id": self.unique_id},
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.post,
            "SYNO.Virtualization.API.Guest.Action",
            "poweroff",
            {"guest_id": self.unique_id},
        )
        await self.coordinator.async_request_refresh()
