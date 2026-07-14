# Datakom D-Series for Home Assistant

Experimental, read-only Home Assistant custom integration for Datakom D500/D502-family generator controllers using the local TCP protocol on port 502.

## Features

- Local polling without Datakom cloud dependency
- Mains and generator voltages, currents and frequencies
- Active, reactive and apparent power
- Power factor per phase and total
- Battery voltage, RPM, oil pressure, temperatures and fuel level
- Run, crank, on-load and engine-hour counters
- Mains, generator and export energy counters
- Operating mode and detailed controller state
- Shutdown, load-dump and warning status
- Optional alarm bits, digital outputs, extension inputs and raw diagnostics

## Safety

This integration is **read-only**. It does not start or stop the generator, change operating mode, reset alarms or write any registers.

The Rainbow/Silent watchdog is intentionally not included.

## Installation with HACS

1. Open HACS.
2. Open **Integrations**.
3. Open the menu and choose **Custom repositories**.
4. Add:

   `https://github.com/KovacDamjan/homeassistant-datakom`

5. Select category **Integration**.
6. Install **Datakom D-Series**.
7. Restart Home Assistant.
8. Open **Settings → Devices & services → Add integration**.
9. Search for **Datakom D-Series**.

Recommended settings for the tested controller:

- Host: `192.168.1.178`
- Port: `502`
- Unit ID: `1`
- Polling interval: `10` seconds

## Supported and tested controller

- Datakom D502 / D500 MK2
- Hardware revision 6
- Firmware 8.7

Other D-series controllers may work but are not yet tested.

## Status

Current release: **0.2.0**

This project is based on protocol analysis of Rainbow Plus traffic and direct testing against a real controller.