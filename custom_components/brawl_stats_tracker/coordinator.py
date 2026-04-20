from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, API_BASE_URL

_LOGGER = logging.getLogger(__name__)


class BrawlStatsCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        api_token: str,
        player_tag: str,
        scan_interval: int,
    ) -> None:
        self.api_token = api_token
        self.player_tag = player_tag.lstrip("#").upper()
        self._session: aiohttp.ClientSession | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.player_tag}",
            update_interval=timedelta(seconds=scan_interval),
        )

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _async_update_data(self) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
        }
        url = f"{API_BASE_URL}/players/%23{self.player_tag}"

        try:
            async with async_timeout.timeout(15):
                session = self._get_session()
                async with session.get(url, headers=headers) as response:
                    if response.status == 403:
                        raise ConfigEntryAuthFailed(
                            "Invalid API key or IP not whitelisted."
                        )
                    if response.status == 404:
                        raise UpdateFailed(f"Player #{self.player_tag} not found.")
                    if response.status != 200:
                        raise UpdateFailed(f"API returned HTTP {response.status}.")
                    raw: dict = await response.json()
        except aiohttp.ClientConnectorError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except TimeoutError as err:
            raise UpdateFailed("Request timed out.") from err

        return self._parse(raw)

    @staticmethod
    def _parse(raw: dict) -> dict:
        club = raw.get("club") or {}
        brawlers = raw.get("brawlers") or []

        return {
            "player_name": raw.get("name", ""),
            "player_tag": raw.get("tag", ""),
            "trophies": raw.get("trophies", 0),
            "highest_trophies": raw.get("highestTrophies", 0),
            "exp_level": raw.get("expLevel", 0),
            "exp_points": raw.get("expPoints", 0),
            "3v3_victories": raw.get("3vs3Victories", 0),
            "solo_victories": raw.get("soloVictories", 0),
            "duo_victories": raw.get("duoVictories", 0),
            "best_robo_rumble_time": raw.get("bestRoboRumbleTime", 0),
            "best_time_as_big_brawler": raw.get("bestTimeAsBigBrawler", 0),
            "brawler_count": len(brawlers),
            "highest_power_play_points": raw.get("highestPowerPlayPoints", 0),
            "is_qualified_championship": raw.get(
                "isQualifiedFromChampionshipChallenge", False
            ),
            "club_name": club.get("name", ""),
        }

    async def async_close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
