from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, CONF_API_TOKEN, CONF_PLAYER_TAGS, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .coordinator import BrawlStatsCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


def _get_tags(entry: ConfigEntry) -> list[str]:
    return entry.options.get(
        CONF_PLAYER_TAGS,
        entry.data.get(CONF_PLAYER_TAGS, []),
    )


def _get_interval(entry: ConfigEntry) -> int:
    return entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api_token = entry.data[CONF_API_TOKEN]
    tags = _get_tags(entry)
    scan_interval = _get_interval(entry)

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"main_{entry.entry_id}")},
        name=entry.title,
        manufacturer="Supercell",
        model="Brawl Stars API",
        entry_type=dr.DeviceEntryType.SERVICE,
        configuration_url="https://developer.brawlstars.com",
    )

    coordinators: dict[str, BrawlStatsCoordinator] = {}

    for tag in tags:
        coordinator = BrawlStatsCoordinator(
            hass=hass,
            api_token=api_token,
            player_tag=tag,
            scan_interval=scan_interval,
        )
        await coordinator.async_config_entry_first_refresh()
        coordinators[tag] = coordinator

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinators: dict[str, BrawlStatsCoordinator] = hass.data[DOMAIN].pop(entry.entry_id)
        for coordinator in coordinators.values():
            await coordinator.async_close()
    return unload_ok
