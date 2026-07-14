from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)


@dataclass(frozen=True, slots=True)
class SensorDefinition:
    key: str
    name: str
    unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    enabled_by_default: bool = True


SENSOR_DEFINITIONS: tuple[SensorDefinition, ...] = (
    SensorDefinition("operation_status", "Operation status"),
    SensorDefinition("unit_mode", "Unit mode"),
    SensorDefinition("mains_voltage_l1", "Mains voltage L1-N", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_voltage_l2", "Mains voltage L2-N", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_voltage_l3", "Mains voltage L3-N", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_voltage_l12", "Mains voltage L1-L2", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_voltage_l23", "Mains voltage L2-L3", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_voltage_l31", "Mains voltage L3-L1", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_voltage_l1", "Genset voltage L1-N", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_voltage_l2", "Genset voltage L2-N", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_voltage_l3", "Genset voltage L3-N", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_voltage_l12", "Genset voltage L1-L2", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_voltage_l23", "Genset voltage L2-L3", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_voltage_l31", "Genset voltage L3-L1", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_current_l1", "Mains current L1", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_current_l2", "Mains current L2", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_current_l3", "Mains current L3", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_current_l1", "Genset current L1", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_current_l2", "Genset current L2", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_current_l3", "Genset current L3", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_active_power_l1", "Mains active power L1", UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_active_power_l2", "Mains active power L2", UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_active_power_l3", "Mains active power L3", UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_active_power", "Mains active power", UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_active_power_l1", "Genset active power L1", UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_active_power_l2", "Genset active power L2", UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_active_power_l3", "Genset active power L3", UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_active_power", "Genset active power", UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_reactive_power", "Mains reactive power", "kvar", None, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_reactive_power", "Genset reactive power", "kvar", None, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_apparent_power", "Mains apparent power", "kVA", None, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_apparent_power", "Genset apparent power", "kVA", None, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_power_factor", "Mains power factor", None, SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_power_factor", "Genset power factor", None, SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT),
    SensorDefinition("mains_frequency", "Mains frequency", UnitOfFrequency.HERTZ, SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_frequency", "Genset frequency", UnitOfFrequency.HERTZ, SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT),
    SensorDefinition("charge_input_voltage", "Charge input voltage", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SensorDefinition("battery_voltage", "Battery voltage", UnitOfElectricPotential.VOLT, SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SensorDefinition("oil_pressure", "Oil pressure", UnitOfPressure.BAR, SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT),
    SensorDefinition("engine_temperature", "Engine temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    SensorDefinition("oil_temperature", "Oil temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, False),
    SensorDefinition("canopy_temperature", "Canopy temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, False),
    SensorDefinition("ambient_temperature", "Ambient temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, False),
    SensorDefinition("fuel_level", "Fuel level", PERCENTAGE, None, SensorStateClass.MEASUREMENT),
    SensorDefinition("engine_rpm", "Engine RPM", "rpm", None, SensorStateClass.MEASUREMENT),
    SensorDefinition("engine_hours", "Engine hours", UnitOfTime.HOURS, SensorDeviceClass.DURATION, SensorStateClass.TOTAL_INCREASING),
    SensorDefinition("hours_since_service", "Hours since service", UnitOfTime.HOURS, SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT),
    SensorDefinition("days_since_service", "Days since service", UnitOfTime.DAYS, SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT),
    SensorDefinition("genset_runs", "Genset runs", None, None, SensorStateClass.TOTAL_INCREASING),
    SensorDefinition("genset_cranks", "Genset cranks", None, None, SensorStateClass.TOTAL_INCREASING),
    SensorDefinition("genset_on_load_count", "Genset on-load count", None, None, SensorStateClass.TOTAL_INCREASING),
    SensorDefinition("genset_active_energy", "Genset active energy", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SensorDefinition("genset_inductive_energy", "Genset inductive energy", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SensorDefinition("genset_capacitive_energy", "Genset capacitive energy", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SensorDefinition("mains_active_energy", "Mains active energy", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SensorDefinition("mains_inductive_energy", "Mains inductive energy", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SensorDefinition("mains_capacitive_energy", "Mains capacitive energy", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SensorDefinition("export_active_energy", "Export active energy", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SensorDefinition("fuel_counter", "Fuel counter", "L", None, SensorStateClass.TOTAL_INCREASING),
)
