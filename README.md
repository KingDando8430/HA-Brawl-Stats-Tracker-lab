[README.md](https://github.com/user-attachments/files/27524281/README.md)
# Brawl Stats Tracker for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
![Version](https://img.shields.io/badge/version-2.0.0-blue)

Track Brawl Stars player statistics directly in Home Assistant.

---

## Features

- Track **multiple players** under a single integration entry per API key
- **Add or remove players** at any time via the Configure button
- **Update the API key** at any time via the **Reconfigure** button (no re-setup needed)
- **Repair notification** when the API key becomes invalid (e.g. after an IP change)
- Each player appears as its own **device** — no bridge/hub device
- New sensors in v2.0:
  - 🏆 **Highest Single Brawler Trophies**
  - 🕐 **Last Battle** (Home Assistant timestamp)
  - 🎮 **Last Battle Mode** (e.g. Duo Showdown, Gem Grab, …)
- Optional **YAML configuration** including auto-generation of API keys
- Multiple entries allowed for multiple API keys

---

## Installation via HACS

1. In HACS → **Integrations** → ⋮ → **Custom repositories**
2. Add: `https://github.com/YOUR_USERNAME/ha-brawl-stats-tracker` — Category: **Integration**
3. Install **Brawl Stats Tracker**
4. Restart Home Assistant

---

## UI Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Brawl Stats Tracker**
3. Enter your API key and player tags

### Getting an API Key

1. Go to [developer.brawlstars.com](https://developer.brawlstars.com/#/account)
2. Create an account or log in
3. Create a new API key — whitelist your **current public IP**
4. Copy the key into the setup dialog

> **Note:** The API key is IP-bound. If your public IP changes, use the **Reconfigure** button on the integration card to enter a new key. A repair notification will appear automatically if the key stops working.

### Managing Players

- **Add/remove players:** Click **Configure** on the integration card
- **Change API key:** Click **Reconfigure** on the integration card

---

## YAML Configuration (optional)

You can configure the integration via `configuration.yaml`. This is useful for automated setups or version-controlled configs.

```yaml
brawl_stats_tracker:
  - api_token: "your_api_key_here"
    player_tags:
      - "#ABC123"
      - "#XYZ456"
    scan_interval: 300  # optional, default 300

  # Second entry with a different API key
  - api_token: "another_api_key"
    player_tags:
      - "#DEF789"
```

### Auto-generate API Key (YAML only)

If you set `autogenerateapi: true`, the integration will automatically log into [developer.brawlstars.com](https://developer.brawlstars.com) and create/refresh an API key whitelisted for your current external IP.

```yaml
brawl_stats_tracker:
  - api_token: ""  # leave empty; will be overwritten automatically
    autogenerateapi: true
    dev_email: "your@email.com"
    dev_password: "your_developer_portal_password"
    external_ip_entity: sensor.external_ip  # entity that holds your current public IP
    player_tags:
      - "#ABC123"
    scan_interval: 300
```

> **Note:** `autogenerateapi` is only available in YAML, not in the UI. The developer portal login uses the unofficial internal API of developer.brawlstars.com and may break if Supercell changes their site.

---

## Sensors

| Sensor | Description | Enabled by default |
|---|---|---|
| Trophies | Current trophy count | ✅ |
| Highest Trophies | All-time highest trophies | ✅ |
| EXP Level | Player experience level | ✅ |
| EXP Points | Total experience points | ✅ |
| 3v3 Victories | Total 3v3 wins | ✅ |
| Solo Showdown Victories | Solo wins | ✅ |
| Duo Showdown Victories | Duo wins | ✅ |
| Best Robo Rumble Time | Best Robo Rumble survival time | ✅ |
| Best Time as Big Brawler | Best Big Brawler survival time | ✅ |
| Unlocked Brawlers | Number of owned brawlers | ✅ |
| **Highest Single Brawler Trophies** | Trophies of best brawler | ✅ |
| **Last Battle** | Timestamp of last match | ✅ |
| **Last Battle Mode** | Mode of last match (e.g. Duo Showdown) | ✅ |
| Highest Power Play Points | Peak Power Play score | ❌ |
| Championship Qualified | Championship challenge status | ❌ |
| Player Name | In-game name | ❌ |
| Player Tag | In-game tag | ❌ |
| Club Name | Current club | ❌ |

---

## License

MIT License — see [LICENSE](LICENSE)
