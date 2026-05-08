from __future__ import annotations

from typing import Any

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    API_BASE_URL,
    CONF_API_TOKEN,
    CONF_PLAYER_TAGS,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_TOKEN): str,
        vol.Required(CONF_PLAYER_TAGS): str,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=60, max=3600)
        ),
    }
)


def _parse_tags(raw: str) -> list[str]:
    return [t.lstrip("#").upper() for t in raw.replace(",", " ").split() if t]


async def _validate_api_token(api_token: str) -> dict[str, str]:
    """Validate that the API token itself is usable (no tag needed)."""
    # We try a known-good endpoint; any valid token should get past 403.
    url = f"{API_BASE_URL}/players/%23PLACEHOLDER"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(10):
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 403:
                        return {"error": "invalid_auth"}
                    # 404 means tag not found but token is valid
                    return {"ok": "true"}
    except (aiohttp.ClientConnectorError, TimeoutError):
        return {"error": "cannot_connect"}
    except Exception:
        return {"error": "unknown"}


async def _validate_tag(api_token: str, tag: str) -> dict[str, str]:
    url = f"{API_BASE_URL}/players/%23{tag}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with async_timeout.timeout(10):
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 403:
                        return {"error": "invalid_auth"}
                    if resp.status == 404:
                        return {"error": "invalid_tag"}
                    if resp.status != 200:
                        return {"error": "cannot_connect"}
                    data = await resp.json()
                    return {"name": data.get("name", tag)}
    except (aiohttp.ClientConnectorError, TimeoutError):
        return {"error": "cannot_connect"}
    except Exception:
        return {"error": "unknown"}


class BrawlStatsTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            tags = _parse_tags(user_input[CONF_PLAYER_TAGS])

            if not tags:
                errors[CONF_PLAYER_TAGS] = "invalid_tag"
            else:
                result = await _validate_tag(user_input[CONF_API_TOKEN], tags[0])

                if "error" in result:
                    errors["base"] = result["error"]
                else:
                    unique_id = f"brawl_stats_{user_input[CONF_API_TOKEN][:8]}"
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

                    entry_count = len(self.hass.config_entries.async_entries(DOMAIN)) + 1

                    return self.async_create_entry(
                        title=f"Brawl Stats Tracker {entry_count:02d}",
                        data={
                            CONF_API_TOKEN: user_input[CONF_API_TOKEN],
                            CONF_PLAYER_TAGS: tags,
                            CONF_SCAN_INTERVAL: user_input.get(
                                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                            ),
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle re-configuration of the API key via the Reconfigure button."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            result = await _validate_api_token(user_input[CONF_API_TOKEN])
            if "error" in result:
                errors["base"] = result["error"]
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={CONF_API_TOKEN: user_input[CONF_API_TOKEN]},
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_TOKEN,
                        default=entry.data.get(CONF_API_TOKEN, ""),
                    ): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "BrawlStatsTrackerOptionsFlow":
        return BrawlStatsTrackerOptionsFlow(config_entry)


class BrawlStatsTrackerOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            new_tags = _parse_tags(user_input[CONF_PLAYER_TAGS])
            if not new_tags:
                errors[CONF_PLAYER_TAGS] = "invalid_tag"
            else:
                api_token = self._config_entry.data[CONF_API_TOKEN]
                # Validate only newly added tags
                existing_tags = set(
                    self._config_entry.options.get(
                        CONF_PLAYER_TAGS,
                        self._config_entry.data.get(CONF_PLAYER_TAGS, []),
                    )
                )
                new_only = [t for t in new_tags if t not in existing_tags]
                for tag in new_only:
                    result = await _validate_tag(api_token, tag)
                    if "error" in result:
                        errors["base"] = result["error"]
                        break

                if not errors:
                    return self.async_create_entry(
                        title="",
                        data={
                            CONF_PLAYER_TAGS: new_tags,
                            CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                        },
                    )

        current_tags = self._config_entry.options.get(
            CONF_PLAYER_TAGS,
            self._config_entry.data.get(CONF_PLAYER_TAGS, []),
        )
        current_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self._config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        tags_str = ", ".join(f"#{t}" for t in current_tags)

        schema = vol.Schema(
            {
                vol.Required(CONF_PLAYER_TAGS, default=tags_str): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                    int, vol.Range(min=60, max=3600)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
