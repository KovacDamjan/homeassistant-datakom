from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .protocol import DatakomTcpClient, s16, u32_low_word_first


OPERATION_STATUS = {
    0: "rest",
    1: "wait_before_fuel",
    2: "preheat",
    3: "wait_oil_pressure",
    4: "crank_rest",
    5: "cranking",
    6: "running_idle",
    7: "engine_heating",
    8: "running_off_load",
    9: "synchronizing_to_mains",
    10: "transfer_to_genset",
    11: "generator_breaker_activation",
    12: "generator_breaker_timer",
    13: "master_on_load",
    14: "peak_lopping",
    15: "power_exporting",
    16: "slave_on_load",
    17: "synchronizing_to_mains_return",
    18: "transfer_to_mains",
    19: "mains_breaker_activation",
    20: "mains_breaker_timer",
    21: "stop_with_cooldown",
    22: "cooling_down",
    23: "stop_idle",
    24: "immediate_stop",
    25: "stopping",
}

UNIT_MODE = {1: "stop", 2: "run", 4: "auto", 8: "test"}


def _firmware_version(raw: int) -> str:
    return f"{(raw >> 4) & 0xF}.{raw & 0xF}"


@dataclass
class DatakomDeviceInfo:
    model: str
    hw_version: int
    sw_version: str


class DatakomApi:
    """Read-only local API for Datakom D-series controllers."""

    def __init__(self, host: str, port: int, unit_id: int) -> None:
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.device_info: DatakomDeviceInfo | None = None

    def test_connection(self) -> DatakomDeviceInfo:
        with DatakomTcpClient(self.host, self.port, self.unit_id, timeout=5) as client:
            regs = client.read_extended(10609, 7).registers

        info = DatakomDeviceInfo(
            model=f"{regs[0]:04X}",
            hw_version=regs[1],
            sw_version=_firmware_version(regs[2]),
        )
        self.device_info = info
        return info

    def read_all(self) -> dict[str, Any]:
        with DatakomTcpClient(self.host, self.port, self.unit_id, timeout=5) as client:
            live = client.read_extended(10240, 164).registers
            alarm_words = client.read_extended(10504, 96).registers
            status = client.read_extended(10604, 12).registers
            counters = client.read_extended(10616, 32).registers
            led_io = client.read_extended(11160, 16).registers
            energy = client.read_extended(11569, 10).registers
            extra_diag = client.read_extended(11648, 32).registers

        def live16(address: int) -> int:
            return live[address - 10240]

        def live_s16(address: int) -> int:
            return s16(live16(address))

        def live32(address: int) -> int:
            idx = address - 10240
            return u32_low_word_first(live[idx : idx + 2])

        def counter32(address: int) -> int:
            idx = address - 10616
            return u32_low_word_first(counters[idx : idx + 2])

        def energy32(address: int) -> int:
            idx = address - 11569
            return u32_low_word_first(energy[idx : idx + 2])

        data: dict[str, Any] = {
            "operation_status_code": status[0],
            "operation_status": OPERATION_STATUS.get(status[0], f"unknown_{status[0]}"),
            "unit_mode_code": status[1],
            "unit_mode": UNIT_MODE.get(status[1], f"unknown_{status[1]}"),
            "device_identity": f"{status[5]:04X}",
            "hardware_version": status[6],
            "software_version": _firmware_version(status[7]),
            "software_version_raw": status[7],
            "mains_voltage_l1": live32(10240) / 10,
            "mains_voltage_l2": live32(10242) / 10,
            "mains_voltage_l3": live32(10244) / 10,
            "genset_voltage_l1": live32(10246) / 10,
            "genset_voltage_l2": live32(10248) / 10,
            "genset_voltage_l3": live32(10250) / 10,
            "mains_voltage_l12": live32(10252) / 10,
            "mains_voltage_l23": live32(10254) / 10,
            "mains_voltage_l31": live32(10256) / 10,
            "genset_voltage_l12": live32(10258) / 10,
            "genset_voltage_l23": live32(10260) / 10,
            "genset_voltage_l31": live32(10262) / 10,
            "mains_current_l1": live32(10264) / 10,
            "mains_current_l2": live32(10266) / 10,
            "mains_current_l3": live32(10268) / 10,
            "genset_current_l1": live32(10270) / 10,
            "genset_current_l2": live32(10272) / 10,
            "genset_current_l3": live32(10274) / 10,
            "mains_active_power_l1": live32(10276) / 10,
            "mains_active_power_l2": live32(10278) / 10,
            "mains_active_power_l3": live32(10280) / 10,
            "genset_active_power_l1": live32(10282) / 10,
            "genset_active_power_l2": live32(10284) / 10,
            "genset_active_power_l3": live32(10286) / 10,
            "mains_active_power": live32(10292) / 10,
            "genset_active_power": live32(10294) / 10,
            "mains_reactive_power_l1": live32(10296) / 10,
            "mains_reactive_power_l2": live32(10298) / 10,
            "mains_reactive_power_l3": live32(10300) / 10,
            "genset_reactive_power_l1": live32(10302) / 10,
            "genset_reactive_power_l2": live32(10304) / 10,
            "genset_reactive_power_l3": live32(10306) / 10,
            "mains_reactive_power": live32(10308) / 10,
            "genset_reactive_power": live32(10310) / 10,
            "mains_apparent_power_l1": live32(10312) / 10,
            "mains_apparent_power_l2": live32(10314) / 10,
            "mains_apparent_power_l3": live32(10316) / 10,
            "genset_apparent_power_l1": live32(10318) / 10,
            "genset_apparent_power_l2": live32(10320) / 10,
            "genset_apparent_power_l3": live32(10322) / 10,
            "mains_apparent_power": live32(10324) / 10,
            "genset_apparent_power": live32(10326) / 10,
            "mains_power_factor_l1": live_s16(10328) / 100,
            "mains_power_factor_l2": live_s16(10329) / 100,
            "mains_power_factor_l3": live_s16(10330) / 100,
            "genset_power_factor_l1": live_s16(10331) / 100,
            "genset_power_factor_l2": live_s16(10332) / 100,
            "genset_power_factor_l3": live_s16(10333) / 100,
            "mains_power_factor": live_s16(10334) / 100,
            "genset_power_factor": live_s16(10335) / 100,
            "mains_frequency": live16(10338) / 100,
            "genset_frequency": live16(10339) / 100,
            "charge_input_voltage": live16(10340) / 100,
            "battery_voltage": live16(10341) / 100,
            "oil_pressure": live16(10361) / 10,
            "engine_temperature": live16(10362) / 10,
            "fuel_level": live16(10363) / 10,
            "oil_temperature": live16(10364) / 10,
            "canopy_temperature": live16(10365) / 10,
            "ambient_temperature": live16(10366) / 10,
            "engine_rpm": live16(10376),
            "genset_runs": counter32(10616),
            "genset_cranks": counter32(10618),
            "genset_on_load_count": counter32(10620),
            "engine_hours": counter32(10622) / 100,
            "hours_since_service": counter32(10624) / 100,
            "days_since_service": counter32(10626) / 100,
            "genset_active_energy": counter32(10628) / 10,
            "genset_inductive_energy": counter32(10630) / 10,
            "genset_capacitive_energy": counter32(10632) / 10,
            "mains_active_energy": energy32(11569) / 10,
            "mains_inductive_energy": energy32(11571) / 10,
            "mains_capacitive_energy": energy32(11573) / 10,
            "export_active_energy": energy32(11575) / 10,
            "fuel_counter": energy32(11577) / 10,
            "engine_running": status[0] not in (0, 24, 25),
            "genset_on_load": status[0] in (13, 14, 15, 16),
            "auto_mode": status[1] == 4,
            "run_mode": status[1] == 2,
            "test_mode": status[1] == 8,
            "stop_mode": status[1] == 1,
            "status_words_raw": list(status),
            "led_status_words_raw": list(led_io[0:4]),
            "digital_output_words_raw": list(led_io[4:7]),
            "extension_input_words_raw": list(led_io[7:9]),
            "alarm_words_raw": list(alarm_words),
            "extra_diagnostics_raw": list(extra_diag),
        }

        shutdown_words = alarm_words[0:16]
        loaddump_words = alarm_words[16:32]
        warning_words = alarm_words[32:48]
        data["shutdown_alarm_active"] = any(shutdown_words)
        data["loaddump_alarm_active"] = any(loaddump_words)
        data["warning_alarm_active"] = any(warning_words)

        for group_name, words in (
            ("shutdown", shutdown_words),
            ("loaddump", loaddump_words),
            ("warning", warning_words),
        ):
            for word_index, word in enumerate(words):
                for bit_index in range(16):
                    data[f"{group_name}_alarm_w{word_index}_b{bit_index}"] = bool(
                        word & (1 << bit_index)
                    )

        for word_index, word in enumerate(led_io[4:7]):
            for bit_index in range(16):
                data[f"digital_output_w{word_index}_b{bit_index}"] = bool(
                    word & (1 << bit_index)
                )

        for word_index, word in enumerate(led_io[7:9]):
            for bit_index in range(16):
                data[f"extension_input_w{word_index}_b{bit_index}"] = bool(
                    word & (1 << bit_index)
                )

        return data
