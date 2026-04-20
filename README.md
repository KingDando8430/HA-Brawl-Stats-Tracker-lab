# Brawl Stats Tracker - Home Assistant Integration

A custom [Home Assistant](https://www.home-assistant.io/) integration that pulls live **Brawl Stars** player statistics from the official [Brawl Stars API](https://developer.brawlstars.com) and exposes them as sensor entities — perfect for dashboards, automations, and family leaderboards.

---

## ✨ Features

- **15 sensors per player** — all from the official Supercell API
- **One entry, multiple players** — add several player tags at once; each player appears as its own child device under the shared entry device
- **Multiple entries supported** — use different API keys or player groups by adding the integration more than once
- **UI-based setup** via Config Flow — no YAML required
- **Players manageable after setup** — add or remove players anytime via ⚙️ Configure
- **Configurable update interval** — per entry, changeable anytime via ⚙️ Configure
- **Re-authentication prompt** when an API key becomes invalid
- **Bilingual** — full German 🇩🇪 and English 🇺🇸 translations

---

## 📊 Sensors

| Sensor | Notes | Enabled by default |
|---|---|---|
| Trophies | Current trophy count | ✅ |
| Highest Trophies | All-time personal record | ✅ |
| EXP Level | Experience level | ✅ |
| EXP Points | Total experience points | ✅ |
| 3v3 Victories | Total wins in 3v3 modes | ✅ |
| Solo Showdown Victories | Total Solo Showdown wins | ✅ |
| Duo Showdown Victories | Total Duo Showdown wins | ✅ |
| Best Robo Rumble Time | Best survival time (minutes) | ✅ |
| Best Time as Big Brawler | Best survival time (seconds) | ✅ |
| Unlocked Brawlers | Number of brawlers owned | ✅ |
| Highest Power Play Points | Legacy field | ❌ |
| Championship Qualified | Boolean | ❌ |
| Player Name | | ❌ |
| Player Tag | | ❌ |
| Club Name | | ❌ |

> Disabled sensors can be enabled individually in the entity settings.

---

## 🔧 Installation

### HACS (recommended)
1. Install Integration via HACS

<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=KingDando8430&repository=HA-Brawl-Stats-Tracker&category=integration" target="_blank" rel="noreferrer noopener"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open your Home Assistant instance and open a repository inside the Home Assistant Community Store." /></a>

2. Restart Home Assistant

<a href="https://my.home-assistant.io/redirect/repairs/" target="_blank" rel="noreferrer noopener"><img src="https://my.home-assistant.io/badges/repairs.svg" alt="Open your Home Assistant instance and show your repairs." /></a>

3. Add integration to Home Assistant

<a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=brawl_stats_tracker" target="_blank" rel="noreferrer noopener"><img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Open your Home Assistant instance and start setting up a new integration." /></a>

### Manual
1. Copy the `custom_components/brawl_stats_tracker/` folder to `/config/custom_components/`
2. Restart Home Assistant
3. Add integration to Home Assistant

---

## ⚙️ Setup

<a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=brawl_stats_tracker" target="_blank" rel="noreferrer noopener"><img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Open your Home Assistant instance and start setting up a new integration." /></a>

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Brawl Stats Tracker**
3. Fill in the form:

| Field | Description |
|---|---|
| API Key | From [developer.brawlstars.com](https://developer.brawlstars.com/#/account) |
| Player Tags | One or more tags, comma-separated — e.g. `#ABC123, #XYZ456` |
| Update interval | Seconds between refreshes (min 60, default 300) |

After setup, the entry is named **Brawl Stats Tracker 01** (or 02, 03 … for additional entries). Each player tag appears as a child device beneath the entry device.

To **add or remove players** or **change the update interval** after setup, click **⚙️ Configure** on the integration card.

### Getting a free API key

1. Visit [developer.brawlstars.com](https://developer.brawlstars.com/#/account)
2. Log in with your Supercell ID
3. Click **New Key**
4. Enter a name and your **current public IP address** (make sure to use the public IP address **of your router**)
5. Copy the generated key

> **Note:** The API key is locked to the IP address you enter. If your router's IP changes, create a new key or update the allowed IP on the developer portal.

---

## 🔄 Multiple Entries

Run the setup again to create a second entry (e.g. with a different API key or a separate group of players). Each entry is numbered automatically: **Brawl Stats Tracker 01**, **Brawl Stats Tracker 02**, …

---

## ⚖️ License

MIT License – see [LICENSE](LICENSE)

> This project is unofficial and is not affiliated with, endorsed, sponsored, or specifically approved by Supercell. For more information see [Supercell's Fan Content Policy](https://supercell.com/en/fan-content-policy/).

---

*Icon: AI-generated image.*
