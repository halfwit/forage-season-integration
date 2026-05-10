"""Sensor platform for Forage Season — one entity per in-season species."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_COMMON_NAME,
    ATTR_ICONIC_TAXON,
    ATTR_INAT_URL,
    ATTR_MONTH,
    ATTR_OBSERVATION_COUNT,
    ATTR_PHOTO_URL,
    ATTR_SCIENTIFIC_NAME,
    ATTR_TAXON_ID,
    ATTR_WIKIPEDIA_URL,
    COORDINATOR,
    DOMAIN,
    INAT_DATA_ATTRIBUTION,
    INAT_PROJECT_NAME,
    INAT_PROJECT_URL,
)
from .coordinator import ForageSeasonCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry. Called once on HA start and on reload."""
    coordinator: ForageSeasonCoordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]

    known_taxon_ids: set[int] = set()

    def _add_new_species() -> None:
        if not coordinator.data:
            return
        new_entities = []
        for species in coordinator.data:
            taxon_id = species["taxon_id"]
            if taxon_id not in known_taxon_ids:
                known_taxon_ids.add(taxon_id)
                new_entities.append(ForageSpeciesSensor(coordinator, entry, species))
        if new_entities:
            async_add_entities(new_entities)

    _add_new_species()
    entry.async_on_unload(coordinator.async_add_listener(_add_new_species))


class ForageSpeciesSensor(CoordinatorEntity, SensorEntity):
    """A sensor representing a single in-season forageable species.

    State: "in_season" or "out_of_season"
    Attributes: photo, scientific name, common name, observation count, links,
                and full attribution to the iNaturalist project.
    """

    def __init__(
        self,
        coordinator: ForageSeasonCoordinator,
        entry: ConfigEntry,
        species: dict,
    ) -> None:
        super().__init__(coordinator)
        self._taxon_id = species["taxon_id"]
        self._entry_id = entry.entry_id
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{self._taxon_id}"
        self._attr_name = species["common_name"]
        self._attr_icon = _icon_for_taxon(species.get("iconic_taxon"))

        # _attr_attribution is the HA-standard key: surfaces in the entity
        # detail panel as a footer and is included in all state exports.
        self._attr_attribution = INAT_DATA_ATTRIBUTION

    @property
    def state(self) -> str:
        """in_season if the species appears in this month's coordinator data."""
        if self.coordinator.data:
            ids = {s["taxon_id"] for s in self.coordinator.data}
            return "in_season" if self._taxon_id in ids else "out_of_season"
        return "unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose rich metadata for the Lovelace card.

        Includes explicit project credit fields so any card or automation
        consuming these entities always has the source URL at hand.
        """
        if not self.coordinator.data:
            return {}
        for species in self.coordinator.data:
            if species["taxon_id"] == self._taxon_id:
                return {
                    ATTR_SCIENTIFIC_NAME: species["scientific_name"],
                    ATTR_COMMON_NAME: species["common_name"],
                    ATTR_TAXON_ID: species["taxon_id"],
                    ATTR_OBSERVATION_COUNT: species["observation_count"],
                    ATTR_PHOTO_URL: species["photo_url"],
                    ATTR_WIKIPEDIA_URL: species["wikipedia_url"],
                    ATTR_INAT_URL: species["inat_url"],
                    ATTR_ICONIC_TAXON: species["iconic_taxon"],
                    ATTR_MONTH: species["month"],
                    # Project credit — always present so any card can link back
                    "data_source": INAT_PROJECT_NAME,
                    "data_source_url": INAT_PROJECT_URL,
                }
        return {}

    @property
    def entity_picture(self) -> str | None:
        """Expose photo URL so HA can display it natively in entity cards."""
        attrs = self.extra_state_attributes
        return attrs.get(ATTR_PHOTO_URL)


def _icon_for_taxon(iconic_taxon: str | None) -> str:
    """Pick an MDI icon based on whether the species is a plant or fungus."""
    if iconic_taxon == "Fungi":
        return "mdi:mushroom"
    if iconic_taxon == "Plantae":
        return "mdi:leaf"
    return "mdi:sprout"
