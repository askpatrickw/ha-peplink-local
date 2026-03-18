# AGENTS.md

This file provides project context for AI coding agents working with this repository.

## Overview

This is a Home Assistant custom integration (`peplink_local`) for monitoring Peplink routers via their local API. It is distributed via HACS and requires Home Assistant 2025.1.0+.

## Architecture

### Data Flow

`PeplinkAPI` (peplink_api.py) → `PeplinkDataUpdateCoordinator` (__init__.py) → platform entities (sensor.py, binary_sensor.py, device_tracker.py)

The coordinator calls five API methods in parallel via `asyncio.gather`:
1. `get_wan_status()` → WAN connection info
2. `get_clients()` → connected client devices
3. `get_system_info()` → combined call returning device info, thermal sensors, fan speeds, system time
4. `get_traffic_stats()` → per-WAN bandwidth rates
5. `get_location()` → GPS data (returns `gps: false` if router has no GPS)

All coordinator data is stored under `hass.data[DOMAIN][entry_id]["coordinator"].data` as a flat dict with keys: `wan_status`, `clients`, `thermal_sensors`, `fan_speeds`, `traffic_stats`, `device_info`, `system_time`, `location_info`.

### API Layer (peplink_api.py)

Two API bases are used:
- **Official API**: `https://{host}/api/` — authentication (`/api/login`), WAN status (`/api/status.wan.connection`), clients (`/api/status.client`)
- **Unofficial CGI API**: `https://{host}/cgi-bin/MANGA/api.cgi?func=<function>&_=<timestamp>` — traffic stats, fan speeds, thermal sensors, device info, GPS location

Authentication uses cookie-based sessions (`bauth` cookie). The `_` parameter in CGI requests is the current Unix timestamp in milliseconds.

### Entity Model

Each WAN connection creates a sub-device (via `via_device`) linked to the main router device. WAN entities use `identifiers={(DOMAIN, f"{entry_id}_wan{wan_id}")}`.

- **sensor.py**: Defines `SENSOR_TYPES` tuple of `PeplinkSensorEntityDescription` (with `value_fn` lambdas). Static sensors (temperature, device info, GPS, fans) use `PeplinkSensor`. Per-WAN sensors use `PeplinkWANSensor`, which routes traffic data from `traffic_stats` and connection data from `wan_status`.
- **binary_sensor.py**: One `connection_status` binary sensor per enabled WAN, checking if `message.startswith("Connected")`.
- **device_tracker.py**: `PeplinkClientTracker` (one per client MAC) + optional `PeplinkGPSTracker` if GPS is available.

## Branch Strategy

This is a fork of [weirded/ha-peplink-local](https://github.com/weirded/ha-peplink-local). Two branches are protected:

- **`main`** — tracks `upstream/main`. Never commit personal changes here. Only sync from upstream.
- **`my-main`** — our release branch (upstream + our changes). Feature branches merge here. This is what gets installed via HACS.

**Workflow:**
- Feature branches → merge into `my-main`
- Upstream contributions → branch from `main`, PR to `upstream/main`
- Upstream sync → pull `upstream/main` into `main`, then merge `main` into `my-main`

**Never push directly to `main` or `my-main`.** Always use feature branches.

## Development Commands

**Run the standalone API test against a real router:**
```bash
# Copy and configure .env first
cp .env.example .env  # or let standalone_test.py generate it
# Then run:
bash tests/run_api_test.sh
# Or directly:
python3 tests/standalone_test.py
```

The test script requires a `.env` file in the project root with:
```
PEPLINK_ROUTER_IP=192.168.1.1
PEPLINK_USERNAME=admin
PEPLINK_PASSWORD=your_password
PEPLINK_VERIFY_SSL=false
```

Test output (raw JSON responses from each API endpoint) is saved to `tests/output/`.

## Gotchas

These are known pitfalls that commonly trip up agents working on this codebase:

- **WAN ID type mismatch**: `traffic_stats["stats"]` uses a string `"wan_id"` field while `wan_status["connection"]` uses an integer `"id"` field. When matching traffic stats to WAN connections, you must convert types for comparison.
- **`get_system_info()` combines four separate CGI calls**: It fetches device info, thermal sensors, fan speeds, and system time in parallel and merges them into a single dict. Don't assume it's a single API call.
- **GPS is conditional**: GPS sensors and the GPS device tracker are only created if `location_info["gps"] == True` AND valid lat/lon values exist. Not all routers have GPS hardware.
- **Fan sensors are dynamic**: Fan sensors are numbered dynamically (fan_1, fan_2, etc.) based on what the router reports. The count varies by hardware model.
- **CGI timestamp parameter**: The `_` parameter in all CGI API requests (`/cgi-bin/MANGA/api.cgi`) MUST be the current Unix timestamp in milliseconds. This is not optional.

## API Documentation

- **Endpoints used by this integration**: See [API.md](API.md) for authentication details, endpoint URLs, and example JSON responses for each API call used.
- **Full Peplink Router API reference**: See [docs/peplink-router-api-8.1.1.md](docs/peplink-router-api-8.1.1.md) for the complete official API documentation covering all available endpoints (firmware 8.1.1). This is useful when exploring endpoints not yet used by the integration.
