# Datakom D-Series for Home Assistant

[![Open your Home Assistant instance and add this repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=KovacDamjan&repository=homeassistant-datakom&category=integration)

[![GitHub Release](https://img.shields.io/github/v/release/KovacDamjan/homeassistant-datakom?style=flat-square)](https://github.com/KovacDamjan/homeassistant-datakom/releases)
[![License](https://img.shields.io/github/license/KovacDamjan/homeassistant-datakom?style=flat-square)](LICENSE)
[![HACS validation](https://img.shields.io/github/actions/workflow/status/KovacDamjan/homeassistant-datakom/hacs.yml?label=HACS&style=flat-square)](https://github.com/KovacDamjan/homeassistant-datakom/actions)
[![Hassfest](https://img.shields.io/github/actions/workflow/status/KovacDamjan/homeassistant-datakom/hassfest.yml?label=Hassfest&style=flat-square)](https://github.com/KovacDamjan/homeassistant-datakom/actions)

Experimental Home Assistant custom integration for Datakom D500/D502-family generator controllers using the local TCP protocol on port 502.

## Datakom Remote Console

<p align="center">
  <img src="docs/images/remote-console.png?v=2" alt="Datakom Remote Console in Home Assistant" width="720">
</p>

The bundled console shows the controller's real physical LCD, live operating state, navigation keypad, status indicators and key generator measurements directly in Home Assistant.

## Features

- Local polling without Datakom cloud dependency
- Real physical 128×64 controller LCD as a Home Assistant camera entity
- Automatically loaded Datakom Remote Console Lovelace card
- Responsive console layout for desktop and mobile
- Visual navigation keypad with Up, Down, Left, Right, OK and ESC
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

The integration currently reads controller data and the physical LCD only. Navigation keys are displayed and animate locally, but do not yet send commands to the controller. Operating-mode commands such as RUN, STOP, AUTO and TEST remain intentionally disabled.

The Rainbow/Silent watchdog is intentionally not included.

## Installation with HACS

Click the **Add to HACS** button above, or add the repository manually:

1. Open HACS.
2. Open **Integrations**.
3. Open the menu and choose **Custom repositories**.
4. Add `https://github.com/KovacDamjan/homeassistant-datakom`.
5. Select category **Integration**.
6. Install **Datakom D-Series**.
7. Restart Home Assistant.
8. Open **Settings → Devices & services → Add integration**.
9. Search for **Datakom D-Series**.

Recommended settings:

- Host: local IP address of your Datakom controller
- Port: `502`
- Unit ID: `1`
- Polling interval: `10` seconds

## Lovelace card

The frontend card is bundled with the integration and loaded automatically. No additional Lovelace JavaScript resource is required.

Add a manual card:

```yaml
type: custom:datakom-card
title: Datakom D502
camera: camera.datakom_d502_lcd_display
entity_prefix: sensor.datakom_d502_
```

Optional LCD refresh interval in milliseconds:

```yaml
type: custom:datakom-card
title: Datakom D502
camera: camera.datakom_d502_lcd_display
entity_prefix: sensor.datakom_d502_
refresh_interval: 10000
```

The console includes:

- the actual physical LCD image,
- online/offline state,
- operation status and unit mode,
- engine-running and on-load state,
- warning and shutdown indicators,
- RPM, fuel, battery voltage and engine temperature,
- a visual Up/Down/Left/Right/OK/ESC keypad,
- TEST/RUN/MAN/AUTO/STOP state indicators.

## Supported and tested controller

- Datakom D502 / D500 MK2
- Hardware revision 6
- Firmware 8.7

Other D-series controllers may work but are not yet tested.

## Development status

Current development version: **0.9.0**

Planned next step: verified, read-only LCD navigation through the controller keypad protocol. Generator operating-mode commands are not a current priority.

This project is based on protocol analysis of Rainbow Plus traffic, static analysis of the Rainbow Plus application and direct testing against a real controller.