from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import DatakomApi
from .const import (
    CONF_SCAN_INTERVAL,
    CONF_UNIT_ID,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UNIT_ID,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import DatakomCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    api = DatakomApi(
        entry.data[CONF_HOST],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
        entry.data.get(CONF_UNIT_ID, DEFAULT_UNIT_ID),
    )

    try:
        await hass.async_add_executor_job(api.test_connection)
    except (OSError, TimeoutError) as err:
        raise ConfigEntryNotReady(
            f"Datakom controller at {api.host}:{api.port} is unreachable"
        ) from err

    coordinator = DatakomCoordinator(
        hass,
        entry,
        api,
        entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        ),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded
