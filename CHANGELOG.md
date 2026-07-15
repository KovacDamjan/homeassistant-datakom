# Changelog

All notable changes to this project will be documented in this file.

The project follows Semantic Versioning for stable releases.

## Unreleased

### Documentation

- Restructured the README for a stable release.
- Added a public roadmap and expanded contribution guidance.

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
