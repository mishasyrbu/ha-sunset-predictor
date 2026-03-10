"""Sensor platform for Sunset Predictor."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunsetPredictorCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sunset Predictor sensor from a config entry."""
    coordinator: SunsetPredictorCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SunsetPredictionSensor(coordinator, entry)])


class SunsetPredictionSensor(CoordinatorEntity, SensorEntity):
    """Sensor for sunset prediction score."""

    _attr_icon = "mdi:weather-sunset"
    _attr_native_unit_of_measurement = "score"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_name = "Sunset Prediction"

    def __init__(
        self,
        coordinator: SunsetPredictorCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_prediction"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Sunset Predictor",
            "manufacturer": "sunset-predictor.com",
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def native_value(self) -> int | None:
        """Return the sunset prediction score."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("score")

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional prediction data as attributes."""
        if self.coordinator.data is None:
            return {}

        data = self.coordinator.data
        raw = data.get("rawFactors", {})
        return {
            # Prediction
            "label": data.get("label"),
            "explanation": data.get("explanation"),
            "confidence": data.get("confidence"),
            "target_date": data.get("targetDate"),
            # Times (ISO 8601 UTC)
            "sunset_time": data.get("sunsetTime"),
            "sunrise_time": data.get("sunriseTime"),
            "timezone": data.get("timezone"),
            # Location
            "location": data.get("location"),
            # Raw weather data
            "cloud_cover": raw.get("cloudCover"),
            "humidity": raw.get("humidity"),
            "visibility": raw.get("visibility"),
            "wind_speed": raw.get("windSpeed"),
            "wind_degree": raw.get("windDegree"),
            "rain_probability": raw.get("rainProb"),
            "condition": raw.get("condition"),
            "temperature": raw.get("temperature"),
            "dew_point": raw.get("dewPoint"),
            "pressure": raw.get("pressure"),
            "aqi": raw.get("aqi"),
        }
