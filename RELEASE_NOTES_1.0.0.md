# Datakom D-Series 1.0.0

The first stable release of the Datakom D-Series integration for Home Assistant.

## Highlights

- Local polling of Datakom D500 MK2 and D502-family generator controllers over TCP port 502.
- Mains, generator, engine, counter, alarm, digital-output and energy entities.
- Bundled live LCD camera and remote navigation keypad.
- Full remote console, standalone LCD card and compact status card.
- Automatic Lovelace resource registration and cache versioning.
- English and Slovenian localization.
- Downloadable diagnostics with sensitive host information redacted.

## Reliability improvements

- Strict validation of Datakom transaction identifiers, MBAP lengths, response sizes and register ranges.
- Communication failures are separated from programming errors.
- Offline controllers are reported as unavailable and recover automatically after communication returns.
- Automated HACS validation, Hassfest and protocol unit tests.
- HACS installation uses the published `datakom.zip` release asset.

## Supported controllers

- Datakom D500 MK2 — tested.
- Datakom D502 — tested.
- Other Datakom D-Series controllers may be compatible but have not yet been verified.

Tested hardware: revision 6, firmware 8.7.

## Safety and limitations

The integration supports monitoring, live LCD display and remote LCD menu navigation. Operating-mode commands such as RUN, STOP, AUTO and TEST are intentionally disabled in this release.

Controller configuration, alarm history and event logs are planned for later releases.

## Upgrade

Install or update through HACS, restart Home Assistant and confirm that the Datakom integration reports version `1.0.0`.
