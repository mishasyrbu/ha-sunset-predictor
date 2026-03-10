"""API client for Sunset Predictor."""

from __future__ import annotations

import logging

import aiohttp

from .const import API_PREDICT_ENDPOINT

_LOGGER = logging.getLogger(__name__)


class SunsetPredictorApiError(Exception):
    """Base exception for API errors."""


class SunsetPredictorAuthError(SunsetPredictorApiError):
    """Authentication error."""


class SunsetPredictorApiClient:
    """Client for the Sunset Predictor API."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str) -> None:
        self._session = session
        self._api_key = api_key

    async def async_get_prediction(
        self, lat: float, lon: float, lang: str
    ) -> dict:
        """Fetch sunset prediction from the API."""
        headers = {"x-api-key": self._api_key}
        params = {"lat": str(lat), "lon": str(lon), "lang": lang}

        try:
            async with self._session.get(
                API_PREDICT_ENDPOINT,
                headers=headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status == 401:
                    raise SunsetPredictorAuthError("Invalid API key")
                resp.raise_for_status()
                return await resp.json()
        except SunsetPredictorAuthError:
            raise
        except aiohttp.ClientError as err:
            raise SunsetPredictorApiError(
                f"Error communicating with API: {err}"
            ) from err

    async def async_validate_key(self, lat: float, lon: float) -> str | None:
        """Test API key validity. Returns None on success, or an error key string."""
        try:
            await self.async_get_prediction(lat, lon, "en")
            return None
        except SunsetPredictorAuthError:
            return "invalid_auth"
        except SunsetPredictorApiError:
            return "cannot_connect"
