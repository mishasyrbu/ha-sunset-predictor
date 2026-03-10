"""DataUpdateCoordinator for Sunset Predictor."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SunsetPredictorApiClient, SunsetPredictorAuthError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SunsetPredictorCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch sunset prediction data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: SunsetPredictorApiClient,
        lat: float,
        lon: float,
        lang: str,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )
        self.api_client = api_client
        self.lat = lat
        self.lon = lon
        self.lang = lang

    async def _async_update_data(self) -> dict:
        """Fetch data from the API."""
        try:
            return await self.api_client.async_get_prediction(
                self.lat, self.lon, self.lang
            )
        except SunsetPredictorAuthError as err:
            raise ConfigEntryAuthFailed from err
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
