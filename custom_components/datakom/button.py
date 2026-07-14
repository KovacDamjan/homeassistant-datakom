from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import DatakomCoordinator
from .entity import DatakomEntity
from .protocol import DatakomTcpClient

KEYPAD_REGISTER = 0x2001


@dataclass(frozen=True, slots=True)
class KeyDefinition:
    key: str
    name: str
    value: int


KEYS: tuple[KeyDefinition, ...] = (
    KeyDefinition("key_up", "Key up", 0x0200),
    KeyDefinition("key_down", "Key down", 0x0400),
    KeyDefinition("key_left", "Key left", 0x0100),
    KeyDefinition("key_right", "Key right", 0x0080),
    # The D500/D502 keypad has four arrows. Rainbow Plus uses right as
    # confirmation/enter and left as escape/back, so these are aliases.
    KeyDefinition("key_ok", "Key OK", 0x0080),
    KeyDefinition("key_esc", "Key ESC", 0x0100),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: DatakomCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DatakomKeyButton(coordinator, definition) for definition in KEYS
    )


class DatakomKeyButton(DatakomEntity, ButtonEntity):
    """A virtual Datakom front-panel navigation key."""

    def __init__(
        self,
        coordinator: DatakomCoordinator,
        definition: KeyDefinition,
    ) -> None:
        super().__init__(coordinator, definition.key)
        self._definition = definition
        self._attr_name = definition.name
        self._attr_icon = {
            "key_up": "mdi:arrow-up-bold-circle",
            "key_down": "mdi:arrow-down-bold-circle",
            "key_left": "mdi:arrow-left-bold-circle",
            "key_right": "mdi:arrow-right-bold-circle",
            "key_ok": "mdi:check-circle",
            "key_esc": "mdi:keyboard-esc",
        }[definition.key]

    async def async_press(self) -> None:
        """Send the exact keypad value used by Rainbow Plus."""

        def _press() -> None:
            with DatakomTcpClient(
                self.coordinator.api.host,
                self.coordinator.api.port,
                self.coordinator.api.unit_id,
                timeout=5,
            ) as client:
                client.write_single_register(
                    KEYPAD_REGISTER,
                    self._definition.value,
                )

        await self.hass.async_add_executor_job(_press)
        self.coordinator.request_lcd_refresh()
