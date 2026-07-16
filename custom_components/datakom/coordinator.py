from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import DatakomApi
from .const import DOMAIN
from .protocol import DatakomProtocolError

_LOGGER = logging.getLogger(__name__)


class DatakomCoordinator(DataUpdateCoordinator[dict]):
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: DatakomApi,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api
        self.lcd_refresh_counter = 0

    def request_lcd_refresh(self) -> None:
        """Invalidate the LCD cache after a remote keypad press."""
        self.lcd_refresh_counter += 1

    async def _async_update_data(self) -> dict:
        try:
            return await self.hass.async_add_executor_job(self.api.read_all)
        except (OSError, TimeoutError, DatakomProtocolError) as err:
            raise UpdateFailed(f"Datakom communication failed: {err}") from err
