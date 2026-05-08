from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_TYPES
from .coordinator import BrawlStatsCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: dict[str, BrawlStatsCoordinator] = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for tag, coordinator in coordinators.items():
        for sensor_key, sensor_cfg in SENSOR_TYPES.items():
            entities.append(
                BrawlStatsSensor(coordinator, entry, sensor_key, sensor_cfg)
            )

    async_add_entities(entities)


class BrawlStatsSensor(CoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator: BrawlStatsCoordinator,
        entry: ConfigEntry,
        sensor_key: str,
        sensor_cfg: dict,
    ) -> None:
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._entry = entry
        self._player_tag = coordinator.player_tag

        self._attr_unique_id = f"brawl_stats_{self._player_tag}_{sensor_key}"
        self._attr_translation_key = sensor_key
        self._attr_has_entity_name = True
        self._attr_icon = sensor_cfg["icon"]
        self._attr_entity_registry_enabled_default = sensor_cfg["enabled_default"]
        self._attr_native_unit_of_measurement = sensor_cfg.get("unit")

        if sensor_cfg.get("state_class"):
            self._attr_state_class = sensor_cfg["state_class"]

        device_class = sensor_cfg.get("device_class")
        if device_class:
            self._attr_device_class = device_class

    def _player_display_name(self) -> str:
        if self.coordinator.data:
            return self.coordinator.data.get("player_name") or self._player_tag
        return self._player_tag

    @property
    def device_info(self) -> dict:
        """Each player is its own device — no bridge/main device."""
        return {
            "identifiers": {(DOMAIN, f"player_{self._player_tag}")},
            "name": self._player_display_name(),
            "manufacturer": "Supercell",
            "model": "Brawl Stars Player",
            "entry_type": "service",
            "configuration_url": f"https://brawltime.ninja/profile/{self._player_tag}",
        }

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        value = self.coordinator.data.get(self._sensor_key)
        # For timestamp sensors HA expects a datetime object
        if self._sensor_key == "last_battle_time":
            if isinstance(value, datetime):
                return value
            return None
        return value

    @property
    def extra_state_attributes(self) -> dict:
        if self._sensor_key != "trophies" or not self.coordinator.data:
            return {}
        data = self.coordinator.data
        attrs: dict = {
            "player_tag": data.get("player_tag"),
            "player_name": data.get("player_name"),
        }
        club = data.get("club_name")
        if club:
            attrs["club"] = club
        return attrs
