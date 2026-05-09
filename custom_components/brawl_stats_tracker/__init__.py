from __future__ import annotations

import logging

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_state_change_event

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
        vol.Required(CONF_PLAYER_TAGS): vol.All(cv.ensure_list, [cv.string]),
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
    {DOMAIN: vol.All(cv.ensure_list, [_INSTANCE_SCHEMA])},
    extra=vol.ALLOW_EXTRA,
)


# ---------------------------------------------------------------------------
# Helper: attempt auto key generation and import as config entry
# ---------------------------------------------------------------------------
async def _try_autogenerate_and_import(
    hass: HomeAssistant,
    instance: dict,
    ip: str,
) -> None:
    """Generate an API key, then create a config entry for this instance."""
    from .auto_api_key import AutoApiKeyError, generate_api_key

    email = instance.get(CONF_DEV_EMAIL, "")
    password = instance.get(CONF_DEV_PASSWORD, "")

    try:
        async with aiohttp.ClientSession() as session:
            api_token = await generate_api_key(
                session,
                email=email,
                password=password,
                external_ip=ip,
            )
        _LOGGER.info("[%s] Auto-generated API key successfully for IP %s.", DOMAIN, ip)
    except AutoApiKeyError as err:
        _LOGGER.error(
            "[%s] Auto key generation failed: %s – using configured api_token fallback.",
            DOMAIN,
            err,
        )
        api_token = instance.get(CONF_API_TOKEN, "")
        if not api_token:
            _LOGGER.error(
                "[%s] No fallback api_token set either. Skipping this instance.", DOMAIN
            )
            return

    tags = [t.lstrip("#").upper() for t in instance[CONF_PLAYER_TAGS]]
    _do_import(hass, api_token, tags, instance.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))


def _do_import(
    hass: HomeAssistant, api_token: str, tags: list[str], scan_interval: int
) -> None:
    """Create a config entry via the import source if one doesn't already exist."""
    unique_id = f"brawl_stats_{api_token[:8]}"
    existing = next(
        (e for e in hass.config_entries.async_entries(DOMAIN) if e.unique_id == unique_id),
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
                    CONF_SCAN_INTERVAL: scan_interval,
                },
            )
        )


# ---------------------------------------------------------------------------
# YAML setup
# ---------------------------------------------------------------------------
async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    instances: list[dict] = config.get(DOMAIN, [])
    if not instances:
        return True

    for instance in instances:
        autogen = instance.get(CONF_AUTOGENERATE_API, False)

        if autogen:
            email = instance.get(CONF_DEV_EMAIL)
            password = instance.get(CONF_DEV_PASSWORD)
            ip_entity = instance.get(CONF_EXTERNAL_IP_ENTITY)

            if not (email and password and ip_entity):
                _LOGGER.error(
                    "[%s] autogenerateapi requires dev_email, dev_password and "
                    "external_ip_entity.",
                    DOMAIN,
                )
                # Fall through to use the configured api_token as-is
                autogen = False

        if autogen:
            ip_state = hass.states.get(ip_entity)
            ip = ip_state.state if ip_state and ip_state.state not in ("unknown", "unavailable") else None

            if ip:
                # IP is already available — generate now
                hass.async_create_task(
                    _try_autogenerate_and_import(hass, instance, ip)
                )
            else:
                # IP not yet available — wait for the entity to become ready
                _LOGGER.info(
                    "[%s] '%s' not yet available. Will auto-generate key once it is.",
                    DOMAIN,
                    ip_entity,
                )

                # Capture instance for the closure
                _instance = dict(instance)
                _ip_entity = ip_entity

                @callback
                def _on_ip_state_change(event):
                    new_state = event.data.get("new_state")
                    if new_state is None or new_state.state in ("unknown", "unavailable"):
                        return
                    _LOGGER.info(
                        "[%s] '%s' now available with IP %s. Generating API key.",
                        DOMAIN,
                        _ip_entity,
                        new_state.state,
                    )
                    hass.async_create_task(
                        _try_autogenerate_and_import(hass, _instance, new_state.state)
                    )
                    # Unsubscribe after first successful fire
                    unsub()

                unsub = async_track_state_change_event(hass, [ip_entity], _on_ip_state_change)
        else:
            # Normal import without autogenerate
            api_token = instance[CONF_API_TOKEN]
            tags = [t.lstrip("#").upper() for t in instance[CONF_PLAYER_TAGS]]
            scan_interval = instance.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            _do_import(hass, api_token, tags, scan_interval)

    return True


# ---------------------------------------------------------------------------
# Config entry setup helpers
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

    # No bridge / main device is registered here.
    # Each player gets its own device in sensor.py via device_info.

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
