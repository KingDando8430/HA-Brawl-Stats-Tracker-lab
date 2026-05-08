from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, API_BASE_URL

_LOGGER = logging.getLogger(__name__)

# ISO-8601 compact format used by Brawl Stars: "20240101T120000.000Z"
_BS_TIME_FORMAT = "%Y%m%dT%H%M%S.%fZ"


def _parse_bs_time(raw: str) -> datetime | None:
    """Parse Brawl Stars compact ISO timestamp to an aware datetime."""
    if not raw:
        return None
    try:
        dt = datetime.strptime(raw, _BS_TIME_FORMAT)
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


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
        player_url = f"{API_BASE_URL}/players/%23{self.player_tag}"
        battle_url = f"{API_BASE_URL}/players/%23{self.player_tag}/battlelog"

        try:
            async with async_timeout.timeout(15):
                session = self._get_session()

                # --- Player profile ---
                async with session.get(player_url, headers=headers) as response:
                    if response.status == 403:
                        # Raises ConfigEntryAuthFailed → HA shows repair notification
                        raise ConfigEntryAuthFailed(
                            "Invalid API key or IP not whitelisted."
                        )
                    if response.status == 404:
                        raise UpdateFailed(f"Player #{self.player_tag} not found.")
                    if response.status != 200:
                        raise UpdateFailed(f"API returned HTTP {response.status}.")
                    raw: dict = await response.json()

                # --- Battle log (best-effort) ---
                battle_data: dict | None = None
                async with session.get(battle_url, headers=headers) as battle_resp:
                    if battle_resp.status == 200:
                        battle_data = await battle_resp.json()

        except ConfigEntryAuthFailed:
            raise
        except aiohttp.ClientConnectorError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except TimeoutError as err:
            raise UpdateFailed("Request timed out.") from err

        return self._parse(raw, battle_data)

    @staticmethod
    def _parse(raw: dict, battle_data: dict | None) -> dict:
        club = raw.get("club") or {}
        brawlers: list[dict] = raw.get("brawlers") or []

        # Highest single-brawler trophy count
        highest_brawler_trophies = max(
            (b.get("highestTrophies", 0) for b in brawlers), default=0
        )

        # Battle log: last battle time & mode
        last_battle_time: datetime | None = None
        last_battle_mode: str | None = None

        if battle_data:
            items: list[dict] = battle_data.get("items") or []
            if items:
                latest = items[0]
                raw_time = latest.get("battleTime", "")
                last_battle_time = _parse_bs_time(raw_time)
                battle_info = latest.get("battle") or {}
                last_battle_mode = battle_info.get("mode") or latest.get("event", {}).get("mode")

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
            "highest_brawler_trophies": highest_brawler_trophies,
            "last_battle_time": last_battle_time,
            "last_battle_mode": last_battle_mode,
            "highest_power_play_points": raw.get("highestPowerPlayPoints", 0),
            "is_qualified_championship": raw.get(
                "isQualifiedFromChampionshipChallenge", False
            ),
            "club_name": club.get("name", ""),
        }

    async def async_close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
