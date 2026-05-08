DOMAIN = "brawl_stats_tracker"
API_BASE_URL = "https://api.brawlstars.com/v1"
DEFAULT_SCAN_INTERVAL = 300

CONF_API_TOKEN = "api_token"
CONF_PLAYER_TAGS = "player_tags"
CONF_SCAN_INTERVAL = "scan_interval"

# YAML-only options
CONF_AUTOGENERATE_API = "autogenerateapi"
CONF_DEV_EMAIL = "dev_email"
CONF_DEV_PASSWORD = "dev_password"
CONF_EXTERNAL_IP_ENTITY = "external_ip_entity"

SENSOR_TYPES: dict[str, dict] = {
    "trophies": {
        "icon": "mdi:trophy",
        "unit": None,
        "enabled_default": True,
        "device_class": None,
        "state_class": "measurement",
    },
    "highest_trophies": {
        "icon": "mdi:trophy-award",
        "unit": None,
        "enabled_default": True,
        "device_class": None,
        "state_class": "measurement",
    },
    "exp_level": {
        "icon": "mdi:star-circle",
        "unit": None,
        "enabled_default": True,
        "device_class": None,
        "state_class": "measurement",
    },
    "exp_points": {
        "icon": "mdi:star-circle-outline",
        "unit": None,
        "enabled_default": True,
        "device_class": None,
        "state_class": "total_increasing",
    },
    "3v3_victories": {
        "icon": "mdi:sword-cross",
        "unit": None,
        "enabled_default": True,
        "device_class": None,
        "state_class": "total_increasing",
    },
    "solo_victories": {
        "icon": "mdi:run-fast",
        "unit": None,
        "enabled_default": True,
        "device_class": None,
        "state_class": "total_increasing",
    },
    "duo_victories": {
        "icon": "mdi:account-multiple",
        "unit": None,
        "enabled_default": True,
        "device_class": None,
        "state_class": "total_increasing",
    },
    "best_robo_rumble_time": {
        "icon": "mdi:robot",
        "unit": "min",
        "enabled_default": True,
        "device_class": None,
        "state_class": "measurement",
    },
    "best_time_as_big_brawler": {
        "icon": "mdi:timer-outline",
        "unit": "s",
        "enabled_default": True,
        "device_class": None,
        "state_class": "measurement",
    },
    "brawler_count": {
        "icon": "mdi:cards",
        "unit": None,
        "enabled_default": True,
        "device_class": None,
        "state_class": "measurement",
    },
    "highest_brawler_trophies": {
        "icon": "mdi:trophy-variant",
        "unit": None,
        "enabled_default": True,
        "device_class": None,
        "state_class": "measurement",
    },
    "last_battle_time": {
        "icon": "mdi:clock-time-five-outline",
        "unit": None,
        "enabled_default": True,
        "device_class": "timestamp",
        "state_class": None,
    },
    "last_battle_mode": {
        "icon": "mdi:gamepad-variant",
        "unit": None,
        "enabled_default": True,
        "device_class": None,
        "state_class": None,
    },
    "highest_power_play_points": {
        "icon": "mdi:lightning-bolt",
        "unit": None,
        "enabled_default": False,
        "device_class": None,
        "state_class": "measurement",
    },
    "is_qualified_championship": {
        "icon": "mdi:certificate",
        "unit": None,
        "enabled_default": False,
        "device_class": None,
        "state_class": None,
    },
    "player_name": {
        "icon": "mdi:account",
        "unit": None,
        "enabled_default": False,
        "device_class": None,
        "state_class": None,
    },
    "player_tag": {
        "icon": "mdi:identifier",
        "unit": None,
        "enabled_default": False,
        "device_class": None,
        "state_class": None,
    },
    "club_name": {
        "icon": "mdi:account-group",
        "unit": None,
        "enabled_default": False,
        "device_class": None,
        "state_class": None,
    },
}
