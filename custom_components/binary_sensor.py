"""Sensor for Syno."""
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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


class VMSensor(CoordinatorEntity, BinarySensorEntity):
    """Sensor vm infos."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, coordinator, unique_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_unique_id = unique_id
        self._attr_name = coordinator.data[unique_id][
            "SYNO.Virtualization.Guest.get_setting"
        ]["name"]

    @property
    def is_on(self):
        """Return status."""
        return True

    @property
    def extra_state_attributes(self):
        """Extra attributes."""
        infos = self.coordinator.data[self.unique_id]
        usbs_list = []
        for key in infos.get("SYNO.Virtualization.Guest.usb_list", {}).get("usbs"):
            usbs_list.append(f"{key.get('product_name')} - id:{key.get('usb_id')}")

        attributes = {
            "usb_list": usbs_list,
            "usb_mounted": infos.get("SYNO.Virtualization.Guest.get_setting", {}).get(
                "usbs"
            ),
        }
        return attributes
