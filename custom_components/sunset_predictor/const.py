"""Constants for the Sunset Predictor integration."""

DOMAIN = "sunset_predictor"
DEFAULT_SCAN_INTERVAL = 120  # minutes (2 hours)
MIN_SCAN_INTERVAL = 30  # minutes
MAX_SCAN_INTERVAL = 180  # minutes (3 hours)
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ru": "Русский",
    "fr": "Français",
    "ro": "Română",
    "uk": "Українська",
    "de": "Deutsch",
    "es": "Español",
}

API_BASE_URL = "https://sunset-predictor.com/api"
API_PREDICT_ENDPOINT = f"{API_BASE_URL}/predict/"
