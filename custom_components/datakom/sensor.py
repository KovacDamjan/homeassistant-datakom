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

_TWO_DECIMAL_KEYS = {
    "battery_voltage",
    "oil_pressure",
    "mains_power_factor",
    "genset_power_factor",
    "mains_current_l1",
    "mains_current_l2",
    "mains_current_l3",
    "genset_current_l1",
    "genset_current_l2",
    "genset_current_l3",
    "mains_active_power_l1",
    "mains_active_power_l2",
    "mains_active_power_l3",
    "mains_active_power",
    "genset_active_power_l1",
    "genset_active_power_l2",
    "genset_active_power_l3",
    "genset_active_power",
    "mains_reactive_power",
    "genset_reactive_power",
    "mains_apparent_power",
    "genset_apparent_power",
    "genset_active_energy",
    "genset_inductive_energy",
    "genset_capacitive_energy",
    "mains_active_energy",
    "mains_inductive_energy",
    "mains_capacitive_energy",
    "export_active_energy",
}

_ONE_DECIMAL_KEYS = {
    "mains_voltage_l1",
    "mains_voltage_l2",
    "mains_voltage_l3",
    "mains_voltage_l12",
    "mains_voltage_l23",
    "mains_voltage_l31",
    "genset_voltage_l1",
    "genset_voltage_l2",
    "genset_voltage_l3",
    "genset_voltage_l12",
    "genset_voltage_l23",
    "genset_voltage_l31",
    "charge_input_voltage",
    "mains_frequency",
    "genset_frequency",
    "engine_temperature",
    "oil_temperature",
    "canopy_temperature",
    "ambient_temperature",
    "fuel_level",
    "engine_hours",
    "fuel_counter",
}

_ICONS = {
    "operation_status": "mdi:information-outline",
    "unit_mode": "mdi:cog-outline",
    "mains_reactive_power": "mdi:sine-wave",
    "genset_reactive_power": "mdi:sine-wave",
    "mains_apparent_power": "mdi:flash-outline",
    "genset_apparent_power": "mdi:flash-outline",
    "fuel_level": "mdi:fuel",
    "engine_rpm": "mdi:engine",
    "genset_runs": "mdi:counter",
    "genset_cranks": "mdi:engine-start",
    "genset_on_load_count": "mdi:counter",
    "fuel_counter": "mdi:fuel",
}


def _suggested_precision(key: str) -> int | None:
    if key in _TWO_DECIMAL_KEYS:
        return 2
    if key in _ONE_DECIMAL_KEYS:
        return 1
    return None


def _description(definition: SensorDefinition) -> SensorEntityDescription:
    return SensorEntityDescription(
        key=definition.key,
        name=definition.name,
        native_unit_of_measurement=definition.unit,
        device_class=definition.device_class,
        state_class=definition.state_class,
        entity_registry_enabled_default=definition.enabled_by_default,
        suggested_display_precision=_suggested_precision(definition.key),
        icon=_ICONS.get(definition.key),
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

        # Keep the controller's hundredth-of-a-volt resolution. Recorder stores
        # the value with two decimals and Home Assistant displays two decimals.
        if key == "battery_voltage" and value is not None:
            return round(float(value), 2)

        return value