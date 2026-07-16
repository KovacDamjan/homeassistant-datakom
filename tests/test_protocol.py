from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "datakom"
    / "protocol.py"
)
SPEC = importlib.util.spec_from_file_location("datakom_protocol", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load Datakom protocol module")

protocol = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = protocol
SPEC.loader.exec_module(protocol)


class FakeClient(protocol.DatakomTcpClient):
    def __init__(self, body: bytes) -> None:
        super().__init__("127.0.0.1")
        self._body = body

    def _exchange(self, transaction_id: int, pdu_with_crc: bytes) -> bytes:
        return self._body


class ProtocolHelpersTest(unittest.TestCase):
    def test_crc_known_modbus_vector(self) -> None:
        self.assertEqual(protocol.modbus_crc16(bytes.fromhex("01030000000A")), 0xCDC5)

    def test_u32_low_word_first(self) -> None:
        self.assertEqual(protocol.u32_low_word_first((0x5678, 0x1234)), 0x12345678)

    def test_s16(self) -> None:
        self.assertEqual(protocol.s16(0x0001), 1)
        self.assertEqual(protocol.s16(0xFFFF), -1)
        self.assertEqual(protocol.s16(0x8000), -32768)

    def test_u32_rejects_wrong_register_count(self) -> None:
        with self.assertRaises(ValueError):
            protocol.u32_low_word_first((1,))


class ExtendedReadValidationTest(unittest.TestCase):
    def test_valid_response(self) -> None:
        client = FakeClient(bytes.fromhex("4304000100020000"))
        result = client.read_extended(100, 2)
        self.assertEqual(result.address, 100)
        self.assertEqual(result.registers, (1, 2))

    def test_rejects_unexpected_function(self) -> None:
        client = FakeClient(bytes.fromhex("0304000100020000"))
        with self.assertRaises(protocol.DatakomProtocolError):
            client.read_extended(100, 2)

    def test_rejects_wrong_declared_byte_count(self) -> None:
        client = FakeClient(bytes.fromhex("430200010000"))
        with self.assertRaises(protocol.DatakomProtocolError):
            client.read_extended(100, 2)

    def test_rejects_short_payload(self) -> None:
        client = FakeClient(bytes.fromhex("430400010000"))
        with self.assertRaises(protocol.DatakomProtocolError):
            client.read_extended(100, 2)

    def test_rejects_invalid_read_arguments(self) -> None:
        client = FakeClient(b"")
        with self.assertRaises(ValueError):
            client.read_extended(-1, 1)
        with self.assertRaises(ValueError):
            client.read_extended(0, 0)


if __name__ == "__main__":
    unittest.main()
