from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import DatakomCoordinator

TO_REDACT = {CONF_HOST}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a Datakom config entry."""
    coordinator: DatakomCoordinator = hass.data[DOMAIN][entry.entry_id]
    info = coordinator.api.device_info

    return {
        "config_entry": async_redact_data(dict(entry.data), TO_REDACT),
        "device": {
            "model": info.model if info else None,
            "hardware_version": info.hw_version if info else None,
            "software_version": info.sw_version if info else None,
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "update_interval_seconds": (
                coordinator.update_interval.total_seconds()
                if coordinator.update_interval is not None
                else None
            ),
        },
        "data": coordinator.data,
    }
