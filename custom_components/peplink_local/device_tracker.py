"""Device tracker platform for Peplink Local integration."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.device_tracker.const import SourceType
from homeassistant.components.device_tracker import ScannerEntity, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _get_clients_from_data(coordinator_data: dict | None) -> list[dict]:
    """Extract the client list from coordinator data safely."""
    if (
        coordinator_data
        and "clients" in coordinator_data
        and "client" in coordinator_data["clients"]
    ):
        return coordinator_data["clients"]["client"]
    return []


def _derive_connection(client: dict) -> str:
    """Derive the connection attribute from a client dict.

    If connectionType is wireless and essid is present, return essid.
    If connectionType is wireless but no essid, return "wireless".
    Otherwise return connectionType as-is (or "unknown").
    """
    conn_type = client.get("connectionType", "unknown")
    if conn_type == "wireless":
        return client.get("essid") or "wireless"
    return conn_type


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up Peplink device tracker based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    _LOGGER.debug(
        "Setting up Peplink device trackers for entry: %s", entry.entry_id
    )

    # Wait for coordinator to get data
    await coordinator.async_config_entry_first_refresh()

    entities = []

    # --- GPS tracker (unchanged) ---
    location_info = coordinator.data.get("location_info", {})
    has_gps = location_info.get("gps", False)
    _LOGGER.debug(
        "GPS capability check for device tracker: %s (has_gps=%s)",
        location_info,
        has_gps,
    )

    if has_gps:
        location_data = location_info.get("location", {})
        if (
            location_data
            and "latitude" in location_data
            and "longitude" in location_data
        ):
            _LOGGER.debug("Creating GPS device tracker for Peplink router")
            entities.append(
                PeplinkGPSTracker(
                    coordinator=coordinator, config_entry_id=entry.entry_id
                )
            )
        else:
            _LOGGER.debug(
                "Router has GPS capability but no valid location data"
            )
    else:
        _LOGGER.debug(
            "Router does not have GPS capability - skipping GPS tracker"
        )

    # --- Dynamic client tracker setup (Group 3) ---

    # 3.1: Store async_add_entities callback and known MAC set for dynamic creation
    known_macs: set[str] = set()
    hass.data[DOMAIN][entry.entry_id]["async_add_entities"] = async_add_entities
    hass.data[DOMAIN][entry.entry_id]["known_macs"] = known_macs

    # 3.2: Create initial PeplinkClientTracker entities for all clients in first refresh
    client_entities = []
    for client in _get_clients_from_data(coordinator.data):
        mac = client.get("mac", "").lower()
        if mac and mac not in known_macs:
            _LOGGER.debug(
                "Creating device tracker for client: %s (%s)",
                client.get("name", "Unknown"),
                mac,
            )
            client_entities.append(
                PeplinkClientTracker(coordinator, entry.entry_id, mac)
            )
            known_macs.add(mac)

    entities.extend(client_entities)

    if entities:
        _LOGGER.debug("Adding %d Peplink device trackers", len(entities))
        async_add_entities(entities, True)
    else:
        _LOGGER.warning("No Peplink device trackers created")

    # 3.3: Register coordinator listener for dynamic entity creation
    @callback
    def _async_check_new_clients() -> None:
        """Compare current MACs against known MACs and add new entities."""
        new_entities = []
        for client in _get_clients_from_data(coordinator.data):
            mac = client.get("mac", "").lower()
            if mac and mac not in known_macs:
                _LOGGER.debug(
                    "Discovered new client: %s (%s)",
                    client.get("name", "Unknown"),
                    mac,
                )
                new_entities.append(
                    PeplinkClientTracker(coordinator, entry.entry_id, mac)
                )
                known_macs.add(mac)
        if new_entities:
            _LOGGER.debug(
                "Dynamically adding %d new client trackers", len(new_entities)
            )
            async_add_entities(new_entities, True)

    entry.async_on_unload(
        coordinator.async_add_listener(_async_check_new_clients)
    )


class PeplinkGPSTracker(CoordinatorEntity, TrackerEntity):
    """Representation of the Peplink router GPS location."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        config_entry_id: str,
    ):
        """Initialize the GPS tracker."""
        super().__init__(coordinator)
        self._config_entry_id = config_entry_id
        self._attr_unique_id = f"{coordinator.host}_gps"
        self._attr_name = "GPS Location"
        self._latitude = None
        self._longitude = None
        self._attributes = {}

        # Update initial state
        self._update_gps_data()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Peplink router."""
        # Get the coordinator
        coordinator = self.coordinator

        # Use device name from API if available
        device_name = coordinator.device_name if hasattr(coordinator, "device_name") and coordinator.device_name else f"Peplink {coordinator.host}" if hasattr(coordinator, "host") else "Peplink"

        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry_id)},
            manufacturer="Peplink",
            model=coordinator.model if hasattr(coordinator, "model") else "Router",
            name=device_name,
            sw_version=coordinator.firmware if hasattr(coordinator, "firmware") else None,
        )

    @property
    def source_type(self) -> str:
        """Return the source type of the device."""
        return SourceType.GPS

    @property
    def latitude(self) -> Optional[float]:
        """Return the latitude of the device."""
        return self._latitude

    @property
    def longitude(self) -> Optional[float]:
        """Return the longitude of the device."""
        return self._longitude

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the device state attributes."""
        return self._attributes

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_gps_data()
        self.async_write_ha_state()

    def _update_gps_data(self) -> None:
        """Update GPS data from the coordinator."""
        self._latitude = None
        self._longitude = None
        self._attributes = {}

        if (
            self.coordinator.data
            and "location_info" in self.coordinator.data
            and "location" in self.coordinator.data["location_info"]
        ):
            location_data = self.coordinator.data["location_info"]["location"]
            self._latitude = location_data.get("latitude")
            self._longitude = location_data.get("longitude")

            # Add accuracy if available
            if "accuracy" in location_data:
                self._attributes["gps_accuracy"] = location_data["accuracy"]

            # Add other attributes that might be useful
            for key, value in location_data.items():
                if key not in ["latitude", "longitude", "accuracy"]:
                    self._attributes[key] = value


class PeplinkClientTracker(CoordinatorEntity, ScannerEntity, RestoreEntity):
    """Representation of a Peplink client device tracker."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        config_entry_id: str,
        client_mac: str,
    ):
        """Initialize the device tracker."""
        super().__init__(coordinator)
        self._client_mac = client_mac.lower()
        self._config_entry_id = config_entry_id
        self._attr_unique_id = f"{config_entry_id}_{self._client_mac}"
        self._is_connected = False
        self._ip_address = None
        self._mac_address = self._client_mac

        # Cached attributes that survive when a client disappears from API
        self._hostname: str = "Unknown"
        self._connection: str = "unknown"
        self._active: bool = False

        # Update initial state from current coordinator data
        self._update_device_data()

    async def async_added_to_hass(self) -> None:
        """Restore last_seen from saved state when entity is added to HA."""
        await super().async_added_to_hass()

        # Restore last_seen from previous state attributes
        state = await self.async_get_last_state()
        if state and state.attributes:
            restored_last_seen = state.attributes.get("last_seen")
            # If the coordinator has no entry for this MAC, write restored
            # value back so inactive clients retain last_seen across restarts
            if (
                restored_last_seen
                and self._client_mac not in self.coordinator.client_last_seen
            ):
                self.coordinator.client_last_seen[self._client_mac] = (
                    restored_last_seen
                )

    @property
    def name(self) -> str:
        """Return the display name of this device."""
        return self._hostname

    @property
    def source_type(self) -> str:
        """Return the source type of the device."""
        return SourceType.ROUTER

    @property
    def is_connected(self) -> bool:
        """Return true if the device is connected to the network."""
        return self._is_connected

    @property
    def ip_address(self) -> Optional[str]:
        """Return the IP address of the device."""
        return self._ip_address

    @property
    def mac_address(self) -> Optional[str]:
        """Return the MAC address of the device."""
        return self._mac_address

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the device state attributes."""
        last_seen = self.coordinator.client_last_seen.get(self._client_mac)
        return {
            "hostname": self._hostname,
            "connection": self._connection,
            "last_seen": last_seen,
            "active": self._active,
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_device_data()
        self.async_write_ha_state()

    def _update_device_data(self) -> None:
        """Update device data from the coordinator."""
        # Search for this MAC in the current client list
        client = self._find_client()

        if client is not None:
            # Client is present in API response — update all fields
            self._is_connected = bool(client.get("connected", False))
            self._ip_address = client.get("ip")
            self._hostname = client.get("name", "Unknown")
            self._connection = _derive_connection(client)
            self._active = self._is_connected
        else:
            # Client absent from API — mark disconnected, preserve cached attrs
            self._is_connected = False
            self._active = False
            # _hostname and _connection retain their last known values

    def _find_client(self) -> Optional[dict]:
        """Find this client's dict in the coordinator data, or None."""
        for client in _get_clients_from_data(self.coordinator.data):
            if client.get("mac", "").lower() == self._client_mac:
                return client
        return None
