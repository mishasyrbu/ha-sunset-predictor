"""Config flow for Sunset Predictor."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .api import SunsetPredictorApiClient
from .const import (
    DEFAULT_LANGUAGE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    SUPPORTED_LANGUAGES,
)

_LOGGER = logging.getLogger(__name__)


class SunsetPredictorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sunset Predictor."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check for duplicate location
            await self.async_set_unique_id(
                f"{user_input['latitude']:.4f}_{user_input['longitude']:.4f}"
            )
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            client = SunsetPredictorApiClient(session, user_input["api_key"])
            error = await client.async_validate_key(
                user_input["latitude"], user_input["longitude"]
            )

            if error is None:
                return self.async_create_entry(
                    title="Sunset Predictor",
                    data=user_input,
                )
            errors["base"] = error

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("api_key"): str,
                    vol.Required(
                        "latitude",
                        default=self.hass.config.latitude,
                    ): cv.latitude,
                    vol.Required(
                        "longitude",
                        default=self.hass.config.longitude,
                    ): cv.longitude,
                    vol.Optional(
                        "language", default=DEFAULT_LANGUAGE
                    ): vol.In(SUPPORTED_LANGUAGES),
                    vol.Optional(
                        "scan_interval", default=DEFAULT_SCAN_INTERVAL
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SunsetPredictorOptionsFlow:
        """Get the options flow."""
        return SunsetPredictorOptionsFlow(config_entry)


class SunsetPredictorOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Sunset Predictor."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = SunsetPredictorApiClient(
                session, self._config_entry.data["api_key"]
            )
            error = await client.async_validate_key(
                user_input["latitude"], user_input["longitude"]
            )
            if error is None:
                return self.async_create_entry(title="", data=user_input)
            errors["base"] = error

        current = self._config_entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "language",
                        default=current.get("language", DEFAULT_LANGUAGE),
                    ): vol.In(SUPPORTED_LANGUAGES),
                    vol.Optional(
                        "scan_interval",
                        default=current.get("scan_interval", DEFAULT_SCAN_INTERVAL),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    ),
                    vol.Required(
                        "latitude",
                        default=current.get("latitude"),
                    ): cv.latitude,
                    vol.Required(
                        "longitude",
                        default=current.get("longitude"),
                    ): cv.longitude,
                }
            ),
            errors=errors,
        )
