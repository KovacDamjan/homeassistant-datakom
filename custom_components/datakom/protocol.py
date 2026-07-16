from __future__ import annotations

import logging
import socket
import struct
from dataclasses import dataclass
from typing import Iterable

_LOGGER = logging.getLogger(__name__)


class DatakomProtocolError(RuntimeError):
    """Raised when a Datakom response violates the expected protocol."""


def modbus_crc16(data: bytes) -> int:
    """Calculate a Modbus CRC-16 checksum."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc & 0xFFFF


@dataclass(frozen=True)
class ReadResult:
    """Decoded Datakom register-read response."""

    address: int
    registers: tuple[int, ...]


class DatakomTcpClient:
    """Synchronous client for the Datakom Modbus/TCP-with-CRC protocol."""

    def __init__(
        self,
        host: str,
        port: int = 502,
        unit_id: int = 1,
        timeout: float = 5.0,
    ) -> None:
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self._sock: socket.socket | None = None

    def connect(self) -> None:
        """Open a TCP connection to the controller."""
        self.close()
        self._sock = socket.create_connection(
            (self.host, self.port), timeout=self.timeout
        )
        self._sock.settimeout(self.timeout)

    def close(self) -> None:
        """Close the TCP connection."""
        if self._sock is not None:
            try:
                self._sock.close()
            finally:
                self._sock = None

    def __enter__(self) -> "DatakomTcpClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _ensure_connected(self) -> socket.socket:
        if self._sock is None:
            raise DatakomProtocolError("Client is not connected")
        return self._sock

    @staticmethod
    def _recv_exact(sock: socket.socket, count: int) -> bytes:
        if count < 0:
            raise DatakomProtocolError(f"Invalid receive length: {count}")

        data = bytearray()
        while len(data) < count:
            chunk = sock.recv(count - len(data))
            if not chunk:
                raise DatakomProtocolError("Connection closed unexpectedly")
            data.extend(chunk)
        return bytes(data)

    def _exchange(self, transaction_id: int, pdu_with_crc: bytes) -> bytes:
        sock = self._ensure_connected()
        expected_transaction = transaction_id & 0xFFFF
        mbap = struct.pack(
            ">HHHB",
            expected_transaction,
            0,
            len(pdu_with_crc) + 1,
            self.unit_id,
        )
        sock.sendall(mbap + pdu_with_crc)

        header = self._recv_exact(sock, 7)
        rx_transaction, protocol_id, length, rx_unit = struct.unpack(
            ">HHHB", header
        )
        if rx_transaction != expected_transaction:
            raise DatakomProtocolError(
                "Unexpected transaction id: "
                f"expected={expected_transaction}, received={rx_transaction}"
            )
        if protocol_id != 0:
            raise DatakomProtocolError(
                f"Unexpected protocol id: {protocol_id}"
            )
        if length < 1:
            raise DatakomProtocolError(f"Invalid MBAP length: {length}")
        if rx_unit != self.unit_id:
            raise DatakomProtocolError(f"Unexpected unit id: {rx_unit}")

        return self._recv_exact(sock, length - 1)

    def read_extended(
        self, address: int, count: int, transaction_id: int = 0x23
    ) -> ReadResult:
        """Read extended Datakom registers."""
        if not 0 <= address <= 0xFFFF:
            raise ValueError("address must fit in one register")
        if not 1 <= count <= 0xFFFF:
            raise ValueError("count must be between 1 and 65535")

        core = struct.pack(">BBHH", self.unit_id, 0x23, address, count)
        crc = struct.pack("<H", modbus_crc16(core))
        body = self._exchange(
            transaction_id,
            bytes([0x23]) + struct.pack(">HH", address, count) + crc,
        )

        if not body or body[0] != 0x43:
            got = body[0] if body else None
            raise DatakomProtocolError(
                f"Unexpected response function: {got}"
            )

        if len(body) < 2:
            raise DatakomProtocolError(
                f"Response too short for byte count: {len(body)}"
            )

        declared = body[1]
        expected_declared = count * 2 + 2
        if declared != expected_declared:
            raise DatakomProtocolError(
                f"Unexpected byte count: declared={declared}, "
                f"expected={expected_declared}"
            )

        expected_body_length = declared + 2
        if len(body) < expected_body_length:
            sock = self._ensure_connected()
            body += self._recv_exact(sock, expected_body_length - len(body))

        if len(body) != expected_body_length:
            raise DatakomProtocolError(
                f"Unexpected response size: expected={expected_body_length}, "
                f"actual={len(body)}"
            )

        register_bytes = body[2:-2]
        if len(register_bytes) != count * 2:
            raise DatakomProtocolError(
                f"Unexpected register payload size: {len(register_bytes)}"
            )

        registers = struct.unpack(f">{count}H", register_bytes)
        return ReadResult(address=address, registers=tuple(registers))

    def write_single_register(
        self, address: int, value: int, transaction_id: int = 0x06
    ) -> None:
        """Write one register using the Datakom Modbus/TCP-with-CRC format.

        The tested D500/D502 returns a five-byte response containing only the
        function, address and value. Some firmware variants may additionally
        append the two-byte RTU CRC, so both response formats are accepted.
        """
        if not 0 <= address <= 0xFFFF:
            raise ValueError("address must fit in one register")
        if not 0 <= value <= 0xFFFF:
            raise ValueError("value must fit in one register")

        core = struct.pack(">BBHH", self.unit_id, 0x06, address, value)
        crc = struct.pack("<H", modbus_crc16(core))
        request = bytes([0x06]) + struct.pack(">HH", address, value) + crc
        body = self._exchange(transaction_id, request)

        _LOGGER.debug(
            "Datakom write response (%d bytes): %s",
            len(body),
            body.hex(" "),
        )

        if len(body) not in (5, 7):
            raise DatakomProtocolError(
                "Unexpected write response "
                f"({len(body)} bytes): {body.hex(' ')}"
            )
        if body[0] != 0x06:
            raise DatakomProtocolError(
                "Unexpected write response function: "
                f"0x{body[0]:02X}; response={body.hex(' ')}"
            )

        response_address, response_value = struct.unpack(">HH", body[1:5])
        if response_address != address or response_value != value:
            raise DatakomProtocolError(
                "Write response did not echo the requested address and value: "
                f"response={body.hex(' ')}"
            )

        if len(body) == 7:
            expected_crc = modbus_crc16(core)
            received_crc = struct.unpack("<H", body[5:7])[0]
            if received_crc != expected_crc:
                raise DatakomProtocolError(
                    f"Write CRC mismatch: expected=0x{expected_crc:04X}, "
                    f"received=0x{received_crc:04X}"
                )


def u32_low_word_first(registers: Iterable[int]) -> int:
    """Decode a two-register unsigned integer with the low word first."""
    regs = tuple(registers)
    if len(regs) != 2:
        raise ValueError("Exactly two registers required")
    return (regs[1] << 16) | regs[0]


def s16(value: int) -> int:
    """Decode a 16-bit signed integer."""
    return value - 0x10000 if value & 0x8000 else value
