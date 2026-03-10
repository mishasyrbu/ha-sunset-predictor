"""The Sunset Predictor integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SunsetPredictorApiClient
from .const import DEFAULT_LANGUAGE, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import SunsetPredictorCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sunset Predictor from a config entry."""
    session = async_get_clientsession(hass)
    api_client = SunsetPredictorApiClient(session, entry.data["api_key"])

    # Options override data for mutable settings
    lang = entry.options.get("language", entry.data.get("language", DEFAULT_LANGUAGE))
    scan_interval = entry.options.get(
        "scan_interval", entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)
    )
    lat = entry.options.get("latitude", entry.data["latitude"])
    lon = entry.options.get("longitude", entry.data["longitude"])

    coordinator = SunsetPredictorCoordinator(
        hass,
        api_client,
        lat=lat,
        lon=lon,
        lang=lang,
        scan_interval=scan_interval,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
