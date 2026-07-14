from __future__ import annotations

import struct
import zlib

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import DatakomCoordinator
from .entity import DatakomEntity
from .protocol import DatakomTcpClient

LCD_ADDRESS = 10648
LCD_REGISTER_COUNT = 64
LCD_WIDTH = 128
LCD_HEIGHT = 64


def _read_lcd_registers(coordinator: DatakomCoordinator) -> tuple[int, ...]:
    """Read the real 128x64 LCD framebuffer from the controller."""
    values: list[int] = []
    with DatakomTcpClient(
        coordinator.api.host,
        coordinator.api.port,
        coordinator.api.unit_id,
        timeout=5,
    ) as client:
        offset = 0
        while offset < LCD_REGISTER_COUNT:
            count = min(36, LCD_REGISTER_COUNT - offset)
            result = client.read_extended(LCD_ADDRESS + offset, count)
            values.extend(result.registers)
            offset += count
    return tuple(values)


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    payload = chunk_type + data
    return (
        struct.pack(">I", len(data))
        + payload
        + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)
    )


def _render_lcd_png(registers: tuple[int, ...]) -> bytes:
    """Render the framebuffer exactly as Rainbow Plus does.

    Each of the 64 registers contains two vertical 8-pixel columns. Registers
    are arranged as 8 pages of 64 registers. The display origin used by the
    controller is bottom-left, therefore the Y axis is inverted.
    """
    if len(registers) != LCD_REGISTER_COUNT:
        raise ValueError(
            f"Expected {LCD_REGISTER_COUNT} LCD registers, got {len(registers)}"
        )

    background = (214, 216, 210)
    foreground = (0, 0, 118)
    pixels = [background] * (LCD_WIDTH * LCD_HEIGHT)

    for page in range(8):
        for column in range(64):
            value = registers[page * 64 + column]
            left_byte = value & 0xFF
            right_byte = (value >> 8) & 0xFF
            x = column * 2

            for bit in range(8):
                y = 63 - page * 8 - bit
                if left_byte & (1 << bit):
                    pixels[y * LCD_WIDTH + x] = foreground
                if right_byte & (1 << bit):
                    pixels[y * LCD_WIDTH + x + 1] = foreground

    raw = bytearray()
    for y in range(LCD_HEIGHT):
        raw.append(0)
        for x in range(LCD_WIDTH):
            raw.extend(pixels[y * LCD_WIDTH + x])

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", LCD_WIDTH, LCD_HEIGHT, 8, 2, 0, 0, 0)
    return (
        signature
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(bytes(raw), level=9))
        + _png_chunk(b"IEND", b"")
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: DatakomCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DatakomLcdCamera(coordinator)])


class DatakomLcdCamera(DatakomEntity, Camera):
    """Camera entity exposing the controller's physical LCD framebuffer."""

    _attr_name = "LCD display"
    _attr_content_type = "image/png"
    _attr_is_streaming = False

    def __init__(self, coordinator: DatakomCoordinator) -> None:
        DatakomEntity.__init__(self, coordinator, "lcd_display")
        Camera.__init__(self)

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        registers = await self.hass.async_add_executor_job(
            _read_lcd_registers, self.coordinator
        )
        return _render_lcd_png(registers)
