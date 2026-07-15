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


_UNAVAILABLE_TEMPERATURE_KEYS = {
    "ambient_temperature",
    "canopy_temperature",
    "oil_temperature",
}

_POWER_FACTOR_KEYS = {
    "genset_power_factor",
    "mains_power_factor",
}



def _description(definition: SensorDefinition) -> SensorEntityDescription:
    return SensorEntityDescription(
        key=definition.key,
        name=definition.name,
        native_unit_of_measurement=definition.unit,
        device_class=definition.device_class,
        state_class=definition.state_class,
        entity_registry_enabled_default=definition.enabled_by_default,
        suggested_display_precision=(1 if definition.key == "battery_voltage" else None),
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
        key = self.entity_description.key
        value = self.coordinator.data.get(key)

        # Datakom uses 0x7FFF as an unavailable/not-configured analog value.
        # The API currently scales temperatures by 0.1, producing 3276.7 °C.
        if key in _UNAVAILABLE_TEMPERATURE_KEYS and value is not None:
            if float(value) >= 3000:
                return None

        # D500/D502 power-factor registers use a scale of 0.001. The API's
        # historic 0.01 scale therefore needs one additional division by ten.
        if key in _POWER_FACTOR_KEYS and value is not None:
            return float(value) / 10

        # Rainbow Plus presents the battery voltage with one decimal place.
        # Return the same precision so Recorder stores 13.5 V instead of 13.46 V
        # and Home Assistant consistently displays one decimal place.
        if key == "battery_voltage" and value is not None:
            return round(float(value), 1)

        return value
