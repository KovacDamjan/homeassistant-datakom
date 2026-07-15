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
    DatakomBinarySensorDescription(
        key="engine_running",
        name="Engine running",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=value("engine_running"),
    ),
    DatakomBinarySensorDescription(
        key="genset_on_load",
        name="Genset on load",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=value("genset_on_load"),
    ),
    DatakomBinarySensorDescription(
        key="auto_mode",
        name="Auto mode",
        value_fn=value("auto_mode"),
    ),
    DatakomBinarySensorDescription(
        key="warning_alarm_active",
        name="Warning alarm",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=value("warning_alarm_active"),
    ),
    DatakomBinarySensorDescription(
        key="shutdown_alarm_active",
        name="Shutdown alarm",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=value("shutdown_alarm_active"),
    ),
    DatakomBinarySensorDescription(
        key="loaddump_alarm_active",
        name="Load dump alarm",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=value("loaddump_alarm_active"),
    ),
    # Rainbow Plus reads the controller's digital-output status words. The
    # first eight physical outputs are bits 0..7 of the first output word.
    # On the tested D502 configuration outputs 1, 2 and 3 are assigned to
    # Crank, Fuel and Coolant Heater respectively.
    DatakomBinarySensorDescription(
        key="digital_output_crank",
        name="Digital output 1 - Crank",
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:engine-start",
        value_fn=value("digital_output_w0_b0"),
    ),
    DatakomBinarySensorDescription(
        key="digital_output_fuel",
        name="Digital output 2 - Fuel",
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:fuel",
        value_fn=value("digital_output_w0_b1"),
    ),
    DatakomBinarySensorDescription(
        key="digital_output_coolant_heater",
        name="Digital output 3 - Coolant heater",
        device_class=BinarySensorDeviceClass.HEAT,
        icon="mdi:radiator",
        value_fn=value("digital_output_w0_b2"),
    ),
    DatakomBinarySensorDescription(
        key="digital_output_4",
        name="Digital output 4",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=value("digital_output_w0_b3"),
    ),
    DatakomBinarySensorDescription(
        key="digital_output_5",
        name="Digital output 5",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=value("digital_output_w0_b4"),
    ),
    DatakomBinarySensorDescription(
        key="digital_output_6",
        name="Digital output 6",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=value("digital_output_w0_b5"),
    ),
    DatakomBinarySensorDescription(
        key="digital_output_7",
        name="Digital output 7",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=value("digital_output_w0_b6"),
    ),
    DatakomBinarySensorDescription(
        key="digital_output_8",
        name="Digital output 8",
        device_class=BinarySensorDeviceClass.POWER,
        value_fn=value("digital_output_w0_b7"),
    ),
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
