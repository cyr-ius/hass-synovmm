"""Sensor for Synology virtual machine energy."""
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

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
        entities.append(VMSensor(coordinator, unique_id, "CPU Usage", "cpu_usage"))
        entities.append(VMSensor(coordinator, unique_id, "MEM Usage", "ram_usage"))

    async_add_entities(entities)


class VMSensor(CoordinatorEntity, SensorEntity):
    """Sensor return power."""

    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator, unique_id, name, value):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.id = unique_id
        self._attr_unique_id = f"{unique_id}_{value}"
        self._attr_name = name
        self.value = value

    @property
    def native_value(self):
        """Max power."""
        stats = self.coordinator.data[self.id].get("stats", {})
        return stats.get(self.value, 0) / 100

    @property
    def device_info(self):
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.id)},
            name=self.coordinator.data[self.id]["guest_name"],
            manufacturer=DOMAIN,
        )
