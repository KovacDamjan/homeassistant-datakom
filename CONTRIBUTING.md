# Contributing

Thank you for helping improve Datakom D-Series for Home Assistant.

## Bug reports

Before opening an issue:

1. Update to the latest release.
2. Restart Home Assistant.
3. Confirm that HACS validation and Hassfest are green for the installed release.
4. Download diagnostics from the Datakom integration.
5. Remove any additional information you consider sensitive before attaching files.

A useful bug report includes:

- Home Assistant version
- Integration version
- Datakom controller model, hardware revision and firmware version
- Clear reproduction steps
- Relevant Home Assistant log entries
- Diagnostics when applicable

## Feature requests

Describe the use case rather than only the requested implementation. For controller write operations, explain the expected safety behaviour and confirmation requirements.

## Pull requests

1. Fork the repository and create a focused feature branch.
2. Follow the existing code style and type hints.
3. Update documentation when behaviour changes.
4. Add or update tests where practical.
5. Run HACS validation and Hassfest before submitting the pull request.
6. Include clear test details in the pull request description.

Do not add unverified register mappings as confirmed facts. Operating-mode write commands must remain disabled unless a change includes explicit safeguards and has been tested on real hardware.

## Compatibility and protocol reports

Include:

- Controller model
- Hardware revision
- Firmware version
- Which entities work or fail
- Relevant Home Assistant logs
- Evidence supporting protocol findings, such as register captures, controller observations or analysis of official software

Clearly distinguish confirmed behaviour from assumptions. Do not publish passwords, cloud credentials or packet captures containing sensitive data.
