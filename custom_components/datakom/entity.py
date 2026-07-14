from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import DatakomCoordinator


class DatakomEntity(CoordinatorEntity[DatakomCoordinator]):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DatakomCoordinator,
        key: str,
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        info = coordinator.api.device_info
        model = info.model if info else "D-Series"
        sw = info.sw_version if info else None
        hw = str(info.hw_version) if info else None

        self._attr_unique_id = (
            f"{coordinator.config_entry.unique_id}_{key}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    coordinator.config_entry.unique_id
                    or coordinator.config_entry.entry_id,
                )
            },
            manufacturer=MANUFACTURER,
            model=model,
            name=f"Datakom {model}",
            sw_version=sw,
            hw_version=hw,
            configuration_url=f"http://{coordinator.api.host}",
        )
