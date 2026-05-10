"""Forage Season — Home Assistant integration.

Queries iNaturalist for edible plants and fungi observed near your home
location during the current month, exposing each species as a sensor entity.
"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import COORDINATOR, DOMAIN
from .coordinator import ForageSeasonCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Forage Season from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Merge data + options so options-flow changes take effect without re-adding
    config = {**entry.data, **entry.options}

    coordinator = ForageSeasonCoordinator(hass, config)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {COORDINATOR: coordinator}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Re-run setup if options change (e.g. radius updated via UI)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
