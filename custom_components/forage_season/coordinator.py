"""DataUpdateCoordinator for Forage Season — fetches iNaturalist data once daily."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MAX_SPECIES,
    CONF_MIN_OBSERVATIONS,
    CONF_RADIUS,
    DEFAULT_MAX_SPECIES,
    DEFAULT_MIN_OBSERVATIONS,
    DEFAULT_RADIUS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    INAT_API_BASE,
    INAT_PROJECT_SLUG,
)

_LOGGER = logging.getLogger(__name__)


class ForageSeasonCoordinator(DataUpdateCoordinator):
    """Fetch and cache in-season forageable species from iNaturalist."""

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=DEFAULT_SCAN_INTERVAL),
        )
        self._lat = config[CONF_LATITUDE]
        self._lon = config[CONF_LONGITUDE]
        self._radius = config.get(CONF_RADIUS, DEFAULT_RADIUS)
        self._min_obs = config.get(CONF_MIN_OBSERVATIONS, DEFAULT_MIN_OBSERVATIONS)
        self._max_species = config.get(CONF_MAX_SPECIES, DEFAULT_MAX_SPECIES)

    async def _async_update_data(self) -> list[dict]:
        """Fetch species counts from iNaturalist for the current month."""
        month = datetime.now().month
        url = f"{INAT_API_BASE}/observations/species_counts"
        params = {
            "project_id": INAT_PROJECT_SLUG,
            "lat": self._lat,
            "lng": self._lon,
            "radius": self._radius,
            "month": month,
            "quality_grade": "research",
            "per_page": 200,
            "order_by": "count",
            "order": "desc",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"iNaturalist returned HTTP {resp.status}")
                    data = await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"iNaturalist request failed: {err}") from err

        results = data.get("results", [])
        species = []

        for entry in results:
            count = entry.get("count", 0)
            if count < self._min_obs:
                # Results are sorted by count desc, so we can break early
                break
            if len(species) >= self._max_species:
                break

            taxon = entry.get("taxon", {})
            if not taxon:
                continue

            # Pull the best available photo
            default_photo = taxon.get("default_photo") or {}
            photo_url = default_photo.get("medium_url") or default_photo.get("url")

            species.append(
                {
                    "taxon_id": taxon.get("id"),
                    "scientific_name": taxon.get("name"),
                    "common_name": taxon.get("preferred_common_name") or taxon.get("name"),
                    "iconic_taxon": taxon.get("iconic_taxon_name"),  # "Plantae", "Fungi", etc.
                    "observation_count": count,
                    "photo_url": photo_url,
                    "wikipedia_url": taxon.get("wikipedia_url"),
                    "inat_url": f"https://www.inaturalist.org/taxa/{taxon.get('id')}",
                    "month": month,
                }
            )

        _LOGGER.debug(
            "Forage Season: found %d in-season species for month=%d at (%s, %s) radius=%skm",
            len(species),
            month,
            self._lat,
            self._lon,
            self._radius,
        )
        return species
