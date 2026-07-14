from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import DatakomCoordinator
from .entity import DatakomEntity


@dataclass(frozen=True, kw_only=True)
class DatakomBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], bool]


def value(key: str) -> Callable[[dict[str, Any]], bool]:
    return lambda data: bool(data.get(key))


BINARY_SENSORS: tuple[DatakomBinarySensorDescription, ...] = (
    DatakomBinarySensorDescription(key="engine_running", name="Engine running", device_class=BinarySensorDeviceClass.RUNNING, value_fn=value("engine_running")),
    DatakomBinarySensorDescription(key="genset_on_load", name="Genset on load", device_class=BinarySensorDeviceClass.POWER, value_fn=value("genset_on_load")),
    DatakomBinarySensorDescription(key="auto_mode", name="Auto mode", value_fn=value("auto_mode")),
    DatakomBinarySensorDescription(key="warning_alarm_active", name="Warning alarm", device_class=BinarySensorDeviceClass.PROBLEM, value_fn=value("warning_alarm_active")),
    DatakomBinarySensorDescription(key="shutdown_alarm_active", name="Shutdown alarm", device_class=BinarySensorDeviceClass.PROBLEM, value_fn=value("shutdown_alarm_active")),
    DatakomBinarySensorDescription(key="loaddump_alarm_active", name="Load dump alarm", device_class=BinarySensorDeviceClass.PROBLEM, value_fn=value("loaddump_alarm_active")),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: DatakomCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DatakomBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
    )


class DatakomBinarySensor(DatakomEntity, BinarySensorEntity):
    entity_description: DatakomBinarySensorDescription

    def __init__(
        self,
        coordinator: DatakomCoordinator,
        description: DatakomBinarySensorDescription,
    ) -> None:
        DatakomEntity.__init__(self, coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool:
        return self.entity_description.value_fn(self.coordinator.data)
