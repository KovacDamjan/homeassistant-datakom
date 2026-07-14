from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import DatakomCoordinator
from .entity import DatakomEntity


@dataclass(frozen=True, kw_only=True)
class DatakomSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]


def value(key: str) -> Callable[[dict[str, Any]], Any]:
    return lambda data: data.get(key)


SENSORS: tuple[DatakomSensorDescription, ...] = (
    DatakomSensorDescription(key="operation_status", name="Operation status", value_fn=value("operation_status")),
    DatakomSensorDescription(key="unit_mode", name="Unit mode", value_fn=value("unit_mode")),
    DatakomSensorDescription(key="mains_frequency", name="Mains frequency", native_unit_of_measurement=UnitOfFrequency.HERTZ, device_class=SensorDeviceClass.FREQUENCY, state_class=SensorStateClass.MEASUREMENT, value_fn=value("mains_frequency")),
    DatakomSensorDescription(key="genset_frequency", name="Genset frequency", native_unit_of_measurement=UnitOfFrequency.HERTZ, device_class=SensorDeviceClass.FREQUENCY, state_class=SensorStateClass.MEASUREMENT, value_fn=value("genset_frequency")),
    DatakomSensorDescription(key="battery_voltage", name="Battery voltage", native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, value_fn=value("battery_voltage")),
    DatakomSensorDescription(key="oil_pressure", name="Oil pressure", native_unit_of_measurement=UnitOfPressure.BAR, device_class=SensorDeviceClass.PRESSURE, state_class=SensorStateClass.MEASUREMENT, value_fn=value("oil_pressure")),
    DatakomSensorDescription(key="engine_temperature", name="Engine temperature", native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, value_fn=value("engine_temperature")),
    DatakomSensorDescription(key="fuel_level", name="Fuel level", native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, value_fn=value("fuel_level")),
    DatakomSensorDescription(key="engine_rpm", name="Engine RPM", native_unit_of_measurement="rpm", state_class=SensorStateClass.MEASUREMENT, value_fn=value("engine_rpm")),
    DatakomSensorDescription(key="engine_hours", name="Engine hours", native_unit_of_measurement=UnitOfTime.HOURS, device_class=SensorDeviceClass.DURATION, state_class=SensorStateClass.TOTAL_INCREASING, value_fn=value("engine_hours")),
    DatakomSensorDescription(key="genset_runs", name="Genset runs", state_class=SensorStateClass.TOTAL_INCREASING, value_fn=value("genset_runs")),
    DatakomSensorDescription(key="genset_cranks", name="Genset cranks", state_class=SensorStateClass.TOTAL_INCREASING, value_fn=value("genset_cranks")),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: DatakomCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(DatakomSensor(coordinator, description) for description in SENSORS)


class DatakomSensor(DatakomEntity, SensorEntity):
    entity_description: DatakomSensorDescription

    def __init__(self, coordinator: DatakomCoordinator, description: DatakomSensorDescription) -> None:
        DatakomEntity.__init__(self, coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)
