from __future__ import annotations

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
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

CARD_URL = "/datakom/datakom-card-v2.js"
CARD_MODULE_URL = f"{CARD_URL}?v=0.9.0"
CARD_REGISTERED = "card_registered"


async def _async_register_card(hass: HomeAssistant) -> None:
    """Expose and automatically load the bundled Lovelace card."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get(CARD_REGISTERED):
        return

    card_path = Path(__file__).parent / "www" / "datakom-card-v2.js"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, str(card_path), cache_headers=False)]
    )
    add_extra_js_url(hass, CARD_MODULE_URL)
    domain_data[CARD_REGISTERED] = True


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    await _async_register_card(hass)

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
