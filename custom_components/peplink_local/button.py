"""Support for Peplink action buttons."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PeplinkDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Peplink button entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]

    entities: list[ButtonEntity] = []

    # Router reboot button (main device)
    entities.append(PeplinkRebootButton(coordinator, api))

    # Per-WAN cellular buttons
    wan_status = coordinator.data.get("wan_status", {})
    wan_connections = wan_status.get("connection", [])

    for connection in wan_connections:
        if connection.get("cellular"):
            wan_id = str(connection.get("id", ""))
            wan_name = connection.get("name", f"WAN {wan_id}")

            wan_device_info = DeviceInfo(
                identifiers={(DOMAIN, f"{config_entry.entry_id}_wan{wan_id}")},
                manufacturer="Peplink",
                model="WAN Connection",
                name=f"{coordinator.device_name or 'Peplink'} WAN{wan_id}",
                via_device=(DOMAIN, config_entry.entry_id),
            )

            entities.append(
                PeplinkCellularResetButton(coordinator, api, wan_id, wan_device_info)
            )
            entities.append(
                PeplinkCellularRescanButton(coordinator, api, wan_id, wan_device_info)
            )

    async_add_entities(entities)


class PeplinkRebootButton(ButtonEntity):
    """Button to reboot the Peplink router."""

    _attr_has_entity_name = True
    _attr_name = "Reboot Router"
    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: PeplinkDataUpdateCoordinator,
        api,
    ) -> None:
        """Initialize the reboot button."""
        self._api = api
        self._attr_unique_id = (
            f"{coordinator.device_name or coordinator.host}_reboot_router"
        )

        device_name = coordinator.device_name or f"Peplink {coordinator.host}"
        model_string = coordinator.model or "Router"
        if coordinator.product_code and coordinator.hardware_revision:
            model_string = f"{model_string} ({coordinator.product_code} HW {coordinator.hardware_revision})"
        elif coordinator.product_code:
            model_string = f"{model_string} ({coordinator.product_code})"
        elif coordinator.hardware_revision:
            model_string = f"{model_string} (HW {coordinator.hardware_revision})"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            manufacturer="Peplink",
            model=model_string,
            name=device_name,
            sw_version=coordinator.firmware,
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Rebooting Peplink router")
        await self._api.reboot_router()


class PeplinkCellularResetButton(ButtonEntity):
    """Button to reset a cellular module on a specific WAN."""

    _attr_has_entity_name = True
    _attr_name = "Reset Cellular Module"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:cellphone-cog"

    def __init__(
        self,
        coordinator: PeplinkDataUpdateCoordinator,
        api,
        wan_id: str,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the cellular reset button."""
        self._api = api
        self._wan_id = wan_id
        self._attr_unique_id = (
            f"{coordinator.device_name or coordinator.host}_wan{wan_id}_reset_cellular_module"
        )
        self._attr_device_info = device_info

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Resetting cellular module on WAN %s", self._wan_id)
        await self._api.reset_cellular_module(self._wan_id)


class PeplinkCellularRescanButton(ButtonEntity):
    """Button to rescan cellular network on a specific WAN."""

    _attr_has_entity_name = True
    _attr_name = "Rescan Cellular Network"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:cellphone-search"

    def __init__(
        self,
        coordinator: PeplinkDataUpdateCoordinator,
        api,
        wan_id: str,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize the cellular rescan button."""
        self._api = api
        self._wan_id = wan_id
        self._attr_unique_id = (
            f"{coordinator.device_name or coordinator.host}_wan{wan_id}_rescan_cellular_network"
        )
        self._attr_device_info = device_info

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Rescanning cellular network on WAN %s", self._wan_id)
        await self._api.rescan_cellular_network(self._wan_id)
