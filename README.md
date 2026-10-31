# Wavin Sentio for Home Assistant

## Requirements
- A Wavin Sentio heated floor controller that is connected to the internet via the RJ45 connector.
- The controller must be added to a Wavin Sentio account. Both things are done via the Wavin Sentio app available in your app store.

## Installation
Files are installed by downloading the files to your custom_components folder directly from here or by adding it via HACS.

Afterwards you can go to the Integrations sections and click the add integration button. Search for Wavin and choose the newly added Wavin Sentio integration.

- First step will ask you to enter you username and password. 
- Second step will ask you to choose the location (controller) you want to add

It will automatically add all the thermostats to your Home Assistant installation and show each one as thermostats in the standard lovelace thermostat UI.

## Sensors
Besides the thermostats, the integration creates per-room sensors (air temperature, humidity and floor temperature, grouped under the room's device) and an outdoor temperature sensor. All of them have `state_class: measurement`, so Home Assistant records long-term statistics.

A `<Room> Dehumidification` binary sensor is created for rooms whose cloud data contains `dehumidifierState` (read-only; shows whether the Sentio system requests dehumidification). The raw value is available in its `dehumidifier_state` attribute and on the room's climate entity. The mapping of raw value to on/off is a placeholder until the real values are known (see `dehumidification_requested` in `binary_sensor.py`).

### Known limitations
- The set of room sensors is decided when the integration is set up. If a sensor appears on the controller later, reload the integration.
- The Wavin library reports 0 for missing values, so a room that reports exactly 0 (e.g. 0 % humidity or 0 °C floor temperature) at setup is treated as having no such sensor and no entity is created for it.

## Changelog
- 2026-10-31 Added per-room Dehumidification binary sensor (dehumidifierState). The wavinsentio library is now vendored as sentio_api.py (no PyPI requirement) to expose this field
- 2026-10-31 Fix vacation/standby switch needing two clicks: wait for the write to finish before refreshing state
- 2026-10-31 Added state_class measurement to room and outdoor temperature sensors (enables long-term statistics)
- 2025-11-25 Fix missing timezone in empty vacationModeUntil by bumping wavinsentio package to 0.5.5
- 2025-08-02 Fix startup problem due to empty vacationModeUntil when never used before
- 2025-08-02 Fix preset, vacation mode, standby mode, cooling mode and outdoor temperature
- 2025-07-03 Major changes for support of v18 - only works with v18 firmware as of now
- 2024-07-09 Removed use of deprecated TEMP_CELSIUS thanks to @https://github.com/201505409 
- 2024-03-05 Changed HVAC logic mode to always be heating
- 2023-12-26 Fixed bug due to new url in API
- 2023-06-25 Fixed bug when having multiple Wavin Sentio controllers same HA instance.
- 2023-05-06 Fixed bug regarding removed async_setup_platforms
- 2023-03-03 Added support for standby switch and refactored existing code
- 2021-12-04 Added support for reauth and outdoor temperature sensor

