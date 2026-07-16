# Datakom D-Series for Home Assistant

[![Open your Home Assistant instance and add this repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=KovacDamjan&repository=homeassistant-datakom&category=integration)

[![GitHub Release](https://img.shields.io/github/v/release/KovacDamjan/homeassistant-datakom?style=flat-square)](https://github.com/KovacDamjan/homeassistant-datakom/releases)
[![License](https://img.shields.io/github/license/KovacDamjan/homeassistant-datakom?style=flat-square)](LICENSE)
[![HACS validation](https://img.shields.io/github/actions/workflow/status/KovacDamjan/homeassistant-datakom/hacs.yml?label=HACS&style=flat-square)](https://github.com/KovacDamjan/homeassistant-datakom/actions)
[![Hassfest](https://img.shields.io/github/actions/workflow/status/KovacDamjan/homeassistant-datakom/hassfest.yml?label=Hassfest&style=flat-square)](https://github.com/KovacDamjan/homeassistant-datakom/actions)
[![Tests](https://img.shields.io/github/actions/workflow/status/KovacDamjan/homeassistant-datakom/tests.yml?label=Tests&style=flat-square)](https://github.com/KovacDamjan/homeassistant-datakom/actions)

Local Home Assistant integration for Datakom D500/D502-family generator controllers using the controller TCP interface on port 502.

## Datakom Remote Console

<p align="center">
  <img src="docs/images/remote-console.png?v=2" alt="Datakom Remote Console in Home Assistant" width="720">
</p>

The bundled console shows the controller's physical LCD, live operating state, working navigation keypad, status indicators and key generator measurements directly in Home Assistant.

## Features

### Monitoring

- Mains and generator voltages, currents and frequencies
- Active, reactive and apparent power
- Power factor per phase and total
- Battery voltage, RPM, oil pressure, temperatures and fuel level
- Run, crank, on-load and engine-hour counters
- Digital output states, including Crank, Fuel and Coolant heater
- Mains, generator and export energy counters
- Operating mode and detailed controller state
- Shutdown, load-dump and warning status

### Remote console

- Physical 128×64 controller LCD as a Home Assistant camera entity
- Working Up, Down, Left, Right, OK and ESC navigation
- Automatic LCD refresh after a key press
- Click-to-enlarge LCD popup
- Animated mains, genset and load-flow indicators
- Responsive desktop and mobile layout

### Home Assistant

- Local polling without a cloud dependency
- Native configuration flow
- HACS installation
- Automatically loaded Lovelace cards without a separate JavaScript resource
- Full Remote Console, standalone LCD card and compact status card
- English by default and Slovenian when Home Assistant uses Slovenian
- Downloadable diagnostics with sensitive host data redacted

## Installation with HACS

Click the **Add to HACS** button above. Until the repository is included in the default HACS catalog, add it manually as a custom repository:

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

- Host: local IP address of the Datakom controller
- Port: `502`
- Unit ID: `1`
- Polling interval: `10` seconds

## Lovelace cards

All cards are bundled with the integration and loaded automatically. No additional Lovelace JavaScript resource is required.

### Full Remote Console

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

### Standalone LCD

```yaml
type: custom:datakom-lcd-card
title: Datakom LCD
camera: camera.datakom_d502_lcd_display
refresh_interval: 5000
```

### Compact status card

```yaml
type: custom:datakom-status-card
title: Datakom status
entity_prefix: sensor.datakom_d502_
```

## Safety

The integration provides read-only monitoring, a live LCD display and remote LCD menu navigation.

Operating-mode commands such as RUN, STOP, AUTO and TEST are disabled in version 1.0.0.

## Known limitations

- Only Datakom D500 MK2 and D502 controllers have been tested directly.
- Controller configuration, alarm history and event logs are not yet available.
- RUN, STOP, AUTO and TEST operating-mode commands are intentionally disabled.
- YAML-mode Lovelace installations use the Home Assistant frontend fallback because integrations cannot modify YAML-defined resources.
- A controller that is offline is reported as unavailable until the next successful polling cycle.

## Roadmap

### v1.1

- Remote operating-mode control with appropriate safety confirmations
- Alarm history
- Event log

### v1.2

- Read-only controller configuration
- Additional diagnostic entities
- Digital input monitoring
- Support for more Datakom D-Series controllers

See [ROADMAP.md](ROADMAP.md) for additional details.

## Supported controllers

| Controller | Status |
|---|---|
| Datakom D500 MK2 | Tested |
| Datakom D502 | Tested |
| Other D-Series controllers | Expected to be compatible, but not yet tested |

Tested hardware: revision 6, firmware 8.7.

## Diagnostics

Open the Datakom integration in **Settings → Devices & services**, select the integration entry and use **Download diagnostics**. The report includes controller identity, firmware, hardware, coordinator state and current decoded values. Sensitive information, including the controller IP address, is automatically redacted.

## Project status

Version 1.0.0 is the first stable release for the tested monitoring and remote LCD-navigation scope. Everyday monitoring is supported on tested Datakom D500 MK2 and D502 controllers.

Bug reports and feature requests are welcome through GitHub Issues.

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

This project is licensed under the terms of the [MIT License](LICENSE).
