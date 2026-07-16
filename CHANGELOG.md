# Changelog

All notable changes to this project will be documented in this file.

The project follows Semantic Versioning for stable releases.

## Unreleased

## 1.0.0 - 2026-07-16

### Added

- Stable local monitoring for tested Datakom D500 MK2 and D502 controllers.
- Native Home Assistant configuration flow and configurable polling interval.
- Electrical, engine, energy, counter, operating-state and alarm entities.
- Live 128×64 controller LCD camera entity.
- Remote LCD navigation using Up, Down, Left, Right, OK and ESC controls.
- Bundled full Remote Console, standalone LCD and compact status Lovelace cards.
- English and Slovenian translations.
- Downloadable diagnostics with sensitive host information redacted.
- HACS brand icon and release ZIP support.
- Protocol unit tests and automated GitHub Actions validation.

### Fixed

- Derived the bundled frontend cache version directly from the integration manifest.
- Limited coordinator error handling to network, timeout and Datakom protocol failures so programming errors are no longer hidden as communication failures.
- Added validation for transaction identifiers, MBAP lengths, response sizes and register request ranges.
- Added validation that HACS release archives contain the required integration files.
- Improved startup handling for malformed or incomplete controller responses.

### Improved

- Configured HACS to install the published `datakom.zip` release asset.
- Hardened the automated GitHub release workflow and ensured releases are published as stable releases.
- Added English and Slovenian names for all exposed sensors.
- Documented supported controllers, known limitations, safety boundaries and release validation.

### Safety

- RUN, STOP, AUTO and TEST operating-mode commands remain intentionally disabled.
- Remote interaction is limited to LCD menu navigation in this release.

## 0.10.6

### Fixed

- Synchronized the bundled frontend cache version with the integration version.
- Improved early frontend card registration to reduce transient Lovelace configuration errors.

### Improved

- Updated digital output state presentation.
- Updated documentation for current features and digital outputs.

## 0.10.5

### Fixed

- Changed the coolant-heater binary sensor presentation to normal on/off states.

## 0.10.4

### Fixed

- Registered the bundled Lovelace card earlier during Home Assistant startup.

## 0.10.3

### Improved

- Battery voltage is stored and presented with two decimal places.

## 0.10.1

### Added

- Digital output binary sensors for Crank, Fuel, Coolant heater and outputs 4–8.

## 0.10.0

### Added

- Working remote LCD navigation.
- Enlarged LCD popup.
- Animated controller indicators and load flow.
- English and Slovenian card localization.
- Expanded diagnostics and documentation.

## 0.2.0

### Added

- Initial public HACS-ready release.
- Local Datakom D500/D502 polling over TCP port 502.
- Electrical, engine, counter, energy, state and alarm entities.
- Optional raw diagnostic, alarm-bit and I/O entities.
