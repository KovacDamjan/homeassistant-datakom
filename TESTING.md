# Pre-release validation

Use this checklist before publishing a stable release.

## Automated checks

- [ ] HACS validation passes.
- [ ] Hassfest passes.
- [ ] Release workflow validates that the tag matches `manifest.json`.
- [ ] Release archive contains `manifest.json`, `__init__.py` and the bundled frontend files.

## Installation and upgrade

- [ ] Clean HACS installation succeeds.
- [ ] Home Assistant starts without Datakom-related errors.
- [ ] Existing installations can upgrade through HACS.
- [ ] The installed integration version matches the GitHub release tag.
- [ ] The bundled Lovelace resource receives the new cache version automatically.
- [ ] No manual JavaScript resource is required in storage-mode Lovelace.

## Controller communication

- [ ] D500 MK2 connection succeeds with the default port and Unit ID.
- [ ] D502 connection succeeds with the default port and Unit ID.
- [ ] All coordinator updates complete at the configured polling interval.
- [ ] Disconnecting the controller makes entities unavailable.
- [ ] Reconnecting the controller restores entities without restarting Home Assistant.
- [ ] Malformed, incomplete or timed-out responses do not crash Home Assistant.

## Entities and diagnostics

- [ ] Main electrical, engine, counter and energy entities report plausible values.
- [ ] Unconfigured analog temperatures are reported as unavailable.
- [ ] Power-factor values use the correct scale.
- [ ] Alarm and digital-output entities update correctly.
- [ ] English and Slovenian entity names load correctly.
- [ ] Downloaded diagnostics redact the controller host address.

## Lovelace cards

- [ ] Full remote console loads after a normal Home Assistant restart.
- [ ] Standalone LCD card loads.
- [ ] Compact status card loads.
- [ ] LCD image refresh works.
- [ ] Navigation buttons work.
- [ ] Cards handle unavailable and unknown entity states without configuration errors.
- [ ] Desktop and mobile layouts remain usable.

## Release approval

- [ ] `CHANGELOG.md` describes all user-visible changes.
- [ ] `README.md` matches current features and limitations.
- [ ] `manifest.json` contains the intended release version.
- [ ] The release tag uses the exact form `vX.Y.Z`.
- [ ] The GitHub release is neither a draft nor a prerelease.
