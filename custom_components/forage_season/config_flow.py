"""Config flow for Forage Season integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MAX_SPECIES,
    CONF_MIN_OBSERVATIONS,
    CONF_RADIUS,
    DEFAULT_MAX_SPECIES,
    DEFAULT_MIN_OBSERVATIONS,
    DEFAULT_RADIUS,
    DOMAIN,
)


def _base_schema(defaults: dict) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_LATITUDE, default=defaults.get(CONF_LATITUDE, 0.0)): vol.Coerce(float),
            vol.Required(CONF_LONGITUDE, default=defaults.get(CONF_LONGITUDE, 0.0)): vol.Coerce(float),
            vol.Optional(CONF_RADIUS, default=defaults.get(CONF_RADIUS, DEFAULT_RADIUS)): vol.All(
                vol.Coerce(int), vol.Range(min=5, max=500)
            ),
            vol.Optional(
                CONF_MIN_OBSERVATIONS,
                default=defaults.get(CONF_MIN_OBSERVATIONS, DEFAULT_MIN_OBSERVATIONS),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
            vol.Optional(
                CONF_MAX_SPECIES,
                default=defaults.get(CONF_MAX_SPECIES, DEFAULT_MAX_SPECIES),
            ): vol.All(vol.Coerce(int), vol.Range(min=5, max=100)),
        }
    )


class ForageSeasonConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the user step — pre-fill with HA's home location."""
        errors: dict[str, str] = {}

        # Pre-fill lat/lon from HA home location
        home_lat = self.hass.config.latitude
        home_lon = self.hass.config.longitude

        if user_input is not None:
            # Prevent duplicate entries for the same coordinates
            await self.async_set_unique_id(
                f"{user_input[CONF_LATITUDE]:.4f}_{user_input[CONF_LONGITUDE]:.4f}"
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Forage Season ({user_input[CONF_LATITUDE]:.2f}, {user_input[CONF_LONGITUDE]:.2f})",
                data=user_input,
            )

        defaults = {
            CONF_LATITUDE: home_lat,
            CONF_LONGITUDE: home_lon,
            CONF_RADIUS: DEFAULT_RADIUS,
            CONF_MIN_OBSERVATIONS: DEFAULT_MIN_OBSERVATIONS,
            CONF_MAX_SPECIES: DEFAULT_MAX_SPECIES,
        }

        return self.async_show_form(
            step_id="user",
            data_schema=_base_schema(defaults),
            errors=errors,
            description_placeholders={
                "project": "edible-flora-fungi-worldwide",
                "inat_url": "https://www.inaturalist.org",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> ForageSeasonOptionsFlow:
        return ForageSeasonOptionsFlow(config_entry)


class ForageSeasonOptionsFlow(config_entries.OptionsFlow):
    """Handle options (radius, thresholds) without re-creating the entry."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Merge data + existing options as defaults
        current = {**self._config_entry.data, **self._config_entry.options}

        return self.async_show_form(
            step_id="init",
            data_schema=_base_schema(current),
        )
