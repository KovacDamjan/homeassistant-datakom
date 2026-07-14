from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import DatakomCoordinator
from .entity import DatakomEntity
from .registers import SENSOR_DEFINITIONS, SensorDefinition


def _description(definition: SensorDefinition) -> SensorEntityDescription:
    return SensorEntityDescription(
        key=definition.key,
        name=definition.name,
        native_unit_of_measurement=definition.unit,
        device_class=definition.device_class,
        state_class=definition.state_class,
        entity_registry_enabled_default=definition.enabled_by_default,
    )


SENSORS: tuple[SensorEntityDescription, ...] = tuple(
    _description(definition) for definition in SENSOR_DEFINITIONS
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: DatakomCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DatakomSensor(coordinator, description) for description in SENSORS
    )


class DatakomSensor(DatakomEntity, SensorEntity):
    entity_description: SensorEntityDescription

    def __init__(
        self,
        coordinator: DatakomCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        DatakomEntity.__init__(self, coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        return self.coordinator.data.get(self.entity_description.key)
