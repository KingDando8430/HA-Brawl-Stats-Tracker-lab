from __future__ import annotations

import logging

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_PLAYER_TAGS,
    CONF_SCAN_INTERVAL,
    CONF_AUTOGENERATE_API,
    CONF_DEV_EMAIL,
    CONF_DEV_PASSWORD,
    CONF_EXTERNAL_IP_ENTITY,
    DEFAULT_SCAN_INTERVAL,
)
from .coordinator import BrawlStatsCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

# ---------------------------------------------------------------------------
# YAML configuration schema
# ---------------------------------------------------------------------------
_INSTANCE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_TOKEN): cv.string,
        vol.Required(CONF_PLAYER_TAGS): vol.All(
            cv.ensure_list, [cv.string]
        ),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=60, max=3600)
        ),
        # YAML-only: auto-generate an API key via developer.brawlstars.com
        vol.Optional(CONF_AUTOGENERATE_API, default=False): cv.boolean,
        vol.Optional(CONF_DEV_EMAIL): cv.string,
        vol.Optional(CONF_DEV_PASSWORD): cv.string,
        # Entity that holds the current external IP (e.g. sensor.external_ip)
        vol.Optional(CONF_EXTERNAL_IP_ENTITY): cv.entity_id,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(cv.ensure_list, [_INSTANCE_SCHEMA]),
    },
    extra=vol.ALLOW_EXTRA,
)


# ---------------------------------------------------------------------------
# YAML setup (creates config entries programmatically)
# ---------------------------------------------------------------------------
async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    instances: list[dict] = config.get(DOMAIN, [])
    if not instances:
        return True

    for instance in instances:
        api_token = instance[CONF_API_TOKEN]
        autogen = instance.get(CONF_AUTOGENERATE_API, False)

        if autogen:
            email = instance.get(CONF_DEV_EMAIL)
            password = instance.get(CONF_DEV_PASSWORD)
            ip_entity = instance.get(CONF_EXTERNAL_IP_ENTITY)

            if not (email and password and ip_entity):
                _LOGGER.error(
                    "[%s] autogenerateapi requires dev_email, dev_password and "
                    "external_ip_entity to be set.",
                    DOMAIN,
                )
            else:
                external_ip = hass.states.get(ip_entity)
                if external_ip is None or external_ip.state in ("unknown", "unavailable"):
                    _LOGGER.warning(
                        "[%s] external_ip_entity '%s' is not available yet; "
                        "skipping auto key generation.",
                        DOMAIN,
                        ip_entity,
                    )
                else:
                    from .auto_api_key import AutoApiKeyError, generate_api_key

                    try:
                        async with aiohttp.ClientSession() as session:
                            api_token = await generate_api_key(
                                session,
                                email=email,
                                password=password,
                                external_ip=external_ip.state,
                            )
                        _LOGGER.info("[%s] Auto-generated API key successfully.", DOMAIN)
                    except AutoApiKeyError as err:
                        _LOGGER.error(
                            "[%s] Auto key generation failed: %s – using configured api_token.",
                            DOMAIN,
                            err,
                        )

        tags = [t.lstrip("#").upper() for t in instance[CONF_PLAYER_TAGS]]
        unique_id = f"brawl_stats_{api_token[:8]}"

        # Check whether a config entry for this key already exists
        existing = next(
            (
                e
                for e in hass.config_entries.async_entries(DOMAIN)
                if e.unique_id == unique_id
            ),
            None,
        )

        if existing is None:
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": "import"},
                    data={
                        CONF_API_TOKEN: api_token,
                        CONF_PLAYER_TAGS: tags,
                        CONF_SCAN_INTERVAL: instance.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    },
                )
            )

    return True


# ---------------------------------------------------------------------------
# Config entry helpers
# ---------------------------------------------------------------------------
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

    # No bridge / main device is registered here intentionally.
    # Each player gets its own device via sensor.py device_info.

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
        coordinators: dict[str, BrawlStatsCoordinator] = hass.data[DOMAIN].pop(
            entry.entry_id
        )
        for coordinator in coordinators.values():
            await coordinator.async_close()
    return unload_ok
