# 🎮 Brawl Stats Tracker

[![GitHub Release][release-badge]][release-url]
[![HACS][hacs-badge]][hacs-url]
[![License][license-badge]][license-url]
[![Home Assistant][ha-badge]][ha-url]

[release-badge]: https://img.shields.io/github/v/release/YOUR_USERNAME/ha-brawl-stats-tracker?style=flat-square
[release-url]: https://github.com/YOUR_USERNAME/ha-brawl-stats-tracker/releases
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square
[hacs-url]: https://github.com/hacs/integration
[license-badge]: https://img.shields.io/github/license/YOUR_USERNAME/ha-brawl-stats-tracker?style=flat-square
[license-url]: LICENSE
[ha-badge]: https://img.shields.io/badge/Home%20Assistant-2023.6%2B-blue?style=flat-square
[ha-url]: https://www.home-assistant.io/

**[🇩🇪 Deutsche Version](#-brawl-stats-tracker--deutsch)**

A custom [Home Assistant](https://www.home-assistant.io/) integration that pulls live **Brawl Stars** player statistics from the official [Brawl Stars API](https://developer.brawlstars.com) and exposes them as sensor entities — perfect for dashboards, automations, and family leaderboards.

---

## ✨ Features

- **15 sensors per player** — all from the official Supercell API, nothing scraped
- **One entry, multiple players** — add several player tags at once; each player appears as its own child device under the shared entry device
- **Multiple entries supported** — use different API keys or player groups by adding the integration more than once
- **UI-based setup** via Config Flow — no YAML required
- **Players manageable after setup** — add or remove players anytime via ⚙️ Configure
- **Configurable update interval** — per entry, changeable anytime via ⚙️ Configure
- **Re-authentication prompt** when an API key becomes invalid
- **Bilingual** — full German 🇩🇪 and English 🇺🇸 translations

---

## 📊 Sensors

| Sensor | Enabled by default | Notes |
|---|---|---|
| Trophies | ✅ | Current trophy count |
| Highest Trophies | ✅ | All-time personal record |
| EXP Level | ✅ | Experience level |
| EXP Points | ✅ | Total experience points |
| 3v3 Victories | ✅ | Total wins in 3v3 modes |
| Solo Showdown Victories | ✅ | Total Solo Showdown wins |
| Duo Showdown Victories | ✅ | Total Duo Showdown wins |
| Best Robo Rumble Time | ✅ | Best survival time (minutes) |
| Best Time as Big Brawler | ✅ | Best survival time (seconds) |
| Unlocked Brawlers | ✅ | Number of brawlers owned |
| Highest Power Play Points | ❌ | Legacy field |
| Championship Qualified | ❌ | Boolean |
| Player Name | ❌ | |
| Player Tag | ❌ | |
| Club Name | ❌ | |

> Disabled sensors can be enabled individually in the entity settings.

---

## 🔧 Installation

### HACS (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](PLACEHOLDER_HACS_LINK)

1. Open **HACS** in Home Assistant
2. Go to **Integrations → ⋮ → Custom repositories**
3. Add `https://github.com/YOUR_USERNAME/ha-brawl-stats-tracker` — category **Integration**
4. Search for **Brawl Stats Tracker** and click **Download**
5. Restart Home Assistant

### Manual

1. Download the [latest release](https://github.com/YOUR_USERNAME/ha-brawl-stats-tracker/releases/latest)
2. Copy the folder `custom_components/brawl_stats_tracker/` into your HA config directory:
   ```
   /config/custom_components/brawl_stats_tracker/
   ```
3. Restart Home Assistant

---

## ⚙️ Setup

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](PLACEHOLDER_CONFIG_FLOW_LINK)

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Brawl Stats Tracker**
3. Fill in the form:

| Field | Description |
|---|---|
| API Key | From [developer.brawlstars.com/#/account](https://developer.brawlstars.com/#/account) |
| Player Tags | One or more tags, comma-separated — e.g. `#ABC123, #XYZ456` |
| Update interval | Seconds between refreshes (min 60, default 300) |

After setup, the entry is named **Brawl Stats Tracker 01** (or 02, 03 … for additional entries). Each player tag appears as a child device beneath the entry device.

To **add or remove players** or **change the update interval** after setup, click **⚙️ Configure** on the integration card.

### Getting a free API key

1. Visit [developer.brawlstars.com/#/account](https://developer.brawlstars.com/#/account)
2. Log in with your Supercell ID
3. Click **New Key**
4. Enter a name and your **current public IP address** (find it at [whatismyip.com](https://whatismyip.com))
5. Copy the generated key

> **Note:** The API key is locked to the IP address you enter. If your router's IP changes (e.g. after a reconnect), create a new key or update the allowed IP on the developer portal.

---

## 🔄 Multiple Entries

Run the setup again to create a second entry (e.g. with a different API key or a separate group of players). Each entry is numbered automatically: **Brawl Stats Tracker 01**, **Brawl Stats Tracker 02**, …

---

## 💡 Automation Examples

**Notify on a new trophy personal best:**
```yaml
automation:
  - alias: "Brawl Stars – New Trophy Record"
    trigger:
      - platform: template
        value_template: >
          {{ states('sensor.playername_trophies') | int >
             states('sensor.playername_highest_trophies') | int }}
    action:
      - service: notify.mobile_app_yourphone
        data:
          message: "🏆 New personal trophy record!"
```

**Daily stats summary at 8 PM:**
```yaml
automation:
  - alias: "Brawl Stars – Daily Stats"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: notify.mobile_app_yourphone
        data:
          message: >
            🎮 {{ states('sensor.playername_trophies') }} trophies |
            {{ states('sensor.playername_3v3_victories') }} 3v3 wins |
            {{ states('sensor.playername_brawler_count') }} brawlers
```

---

## 🤝 Contributing

Issues and pull requests are welcome. Please open an issue first for larger changes.

---

## ⚖️ License

[MIT](LICENSE) © YOUR_USERNAME

> This project is not affiliated with, endorsed, sponsored, or specifically approved by Supercell. For more information see [Supercell's Fan Content Policy](https://supercell.com/en/fan-content-policy/).

---
---

# 🎮 Brawl Stats Tracker — Deutsch

**[🇬🇧 English version above](#-brawl-stats-tracker)**

Eine Custom Integration für [Home Assistant](https://www.home-assistant.io/), die Live-Statistiken von Brawl Stars-Spielern über die offizielle [Brawl Stars API](https://developer.brawlstars.com) abruft und als Sensor-Entitäten bereitstellt — ideal für Dashboards, Automationen und Familien-Bestenlisten.

---

## ✨ Funktionen

- **15 Sensoren pro Spieler** — direkt von der offiziellen Supercell-API, kein Scraping
- **Ein Eintrag, mehrere Spieler** — mehrere Spieler-Tags auf einmal eingeben; jeder Spieler erscheint als eigenes Child-Device unter dem Eintrag
- **Mehrere Einträge möglich** — verschiedene API-Schlüssel oder Spielergruppen durch erneutes Hinzufügen der Integration
- **UI-basierte Einrichtung** via Config Flow — kein YAML nötig
- **Spieler nachträglich verwaltbar** — Spieler jederzeit über ⚙️ Konfigurieren hinzufügen oder entfernen
- **Konfigurierbares Aktualisierungsintervall** — pro Eintrag, jederzeit über ⚙️ Konfigurieren änderbar
- **Re-Auth-Hinweis** wenn ein API-Schlüssel ungültig wird
- **Zweisprachig** — vollständige Übersetzungen auf Deutsch 🇩🇪 und Englisch 🇺🇸

---

## 📊 Sensoren

| Sensor | Standard aktiv | Hinweis |
|---|---|---|
| Trophäen | ✅ | Aktuelle Trophäenzahl |
| Höchste Trophäen | ✅ | Persönlicher Allzeithöchstand |
| EXP-Level | ✅ | Erfahrungslevel |
| EXP-Punkte | ✅ | Gesamte Erfahrungspunkte |
| 3v3-Siege | ✅ | Gesamtsiege in 3v3-Modi |
| Solo Showdown-Siege | ✅ | Gesamtsiege im Solo Showdown |
| Duo Showdown-Siege | ✅ | Gesamtsiege im Duo Showdown |
| Beste Robo-Rumble-Zeit | ✅ | Beste Überlebenszeit (Minuten) |
| Beste Zeit als Big Brawler | ✅ | Beste Überlebenszeit (Sekunden) |
| Freigeschaltete Brawler | ✅ | Anzahl der Brawler im Besitz |
| Höchste Power-Play-Punkte | ❌ | Legacy-Feld |
| Championship-Qualifiziert | ❌ | Boolean |
| Spielername | ❌ | |
| Spieler-Tag | ❌ | |
| Club-Name | ❌ | |

> Deaktivierte Sensoren können in den Entitäts-Einstellungen einzeln aktiviert werden.

---

## 🔧 Installation

### HACS (empfohlen)

[![Öffne Home Assistant und füge ein HACS-Repository hinzu.](https://my.home-assistant.io/badges/hacs_repository.svg)](PLACEHOLDER_HACS_LINK)

1. **HACS** in Home Assistant öffnen
2. **Integrationen → ⋮ → Benutzerdefinierte Repositories**
3. `https://github.com/YOUR_USERNAME/ha-brawl-stats-tracker` hinzufügen — Kategorie **Integration**
4. Nach **Brawl Stats Tracker** suchen und **Herunterladen** klicken
5. Home Assistant neu starten

### Manuell

1. Neueste Version von der [Releases-Seite](https://github.com/YOUR_USERNAME/ha-brawl-stats-tracker/releases/latest) herunterladen
2. Ordner `custom_components/brawl_stats_tracker/` in das HA-Konfigurationsverzeichnis kopieren:
   ```
   /config/custom_components/brawl_stats_tracker/
   ```
3. Home Assistant neu starten

---

## ⚙️ Einrichtung

[![Öffne Home Assistant und richte eine neue Integration ein.](https://my.home-assistant.io/badges/config_flow_start.svg)](PLACEHOLDER_CONFIG_FLOW_LINK)

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. Nach **Brawl Stats Tracker** suchen
3. Formular ausfüllen:

| Feld | Beschreibung |
|---|---|
| API-Schlüssel | Von [developer.brawlstars.com/#/account](https://developer.brawlstars.com/#/account) |
| Spieler-Tags | Ein oder mehrere Tags, kommagetrennt — z.B. `#ABC123, #XYZ456` |
| Aktualisierungsintervall | Sekunden zwischen Updates (min. 60, Standard 300) |

Nach dem Setup heißt der Eintrag **Brawl Stats Tracker 01** (oder 02, 03 … für weitere Einträge). Jeder Spieler-Tag erscheint als Child-Device unter dem Eintrag-Gerät.

Zum **Hinzufügen oder Entfernen von Spielern** oder zum **Ändern des Intervalls** nach dem Setup auf **⚙️ Konfigurieren** auf der Integrationskarte klicken.

### Kostenloser API-Schlüssel

1. [developer.brawlstars.com/#/account](https://developer.brawlstars.com/#/account) aufrufen
2. Mit Supercell-ID einloggen
3. **New Key** klicken
4. Namen und aktuelle öffentliche IP-Adresse eingeben (findest du auf [whatismyip.com](https://whatismyip.com))
5. Generierten Schlüssel kopieren

> **Hinweis:** Der API-Schlüssel ist an die eingetragene IP gebunden. Ändert sich die IP des Routers, muss ein neuer Schlüssel erstellt oder die erlaubte IP im Developer-Portal aktualisiert werden.

---

## 🔄 Mehrere Einträge

Integration erneut hinzufügen für einen zweiten Eintrag (z.B. mit anderem API-Schlüssel oder anderer Spielergruppe). Einträge werden automatisch nummeriert: **Brawl Stats Tracker 01**, **Brawl Stats Tracker 02**, …

---

## 💡 Automations-Beispiele

**Benachrichtigung bei neuem Trophäen-Rekord:**
```yaml
automation:
  - alias: "Brawl Stars – Neuer Trophäen-Rekord"
    trigger:
      - platform: template
        value_template: >
          {{ states('sensor.spielername_trophäen') | int >
             states('sensor.spielername_höchste_trophäen') | int }}
    action:
      - service: notify.mobile_app_deinhandy
        data:
          message: "🏆 Neuer persönlicher Trophäen-Rekord!"
```

**Tägliche Stats-Zusammenfassung um 20 Uhr:**
```yaml
automation:
  - alias: "Brawl Stars – Tägliche Stats"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: notify.mobile_app_deinhandy
        data:
          message: >
            🎮 {{ states('sensor.spielername_trophäen') }} Trophäen |
            {{ states('sensor.spielername_3v3_siege') }} 3v3-Siege |
            {{ states('sensor.spielername_freigeschaltete_brawler') }} Brawler
```

---

## 🤝 Beitragen

Issues und Pull Requests sind willkommen. Bitte vorher ein Issue für größere Änderungen öffnen.

---

## ⚖️ Lizenz

[MIT](LICENSE) © YOUR_USERNAME

> Dieses Projekt ist nicht mit Supercell verbunden und wird nicht von Supercell unterstützt. Weitere Informationen in der [Supercell Fan Content Policy](https://supercell.com/en/fan-content-policy/).
