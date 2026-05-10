"""Constants for the Forage Season integration."""

DOMAIN = "forage_season"

# iNaturalist
INAT_API_BASE = "https://api.inaturalist.org/v1"
INAT_PROJECT_SLUG = "edible-flora-fungi-worldwide"
INAT_PROJECT_URL = "https://www.inaturalist.org/projects/edible-flora-fungi-worldwide"
INAT_PROJECT_NAME = "Edible Flora & Fungi Worldwide"
INAT_DATA_ATTRIBUTION = (
    "Data © iNaturalist contributors via the "
    "\u201cEdible Flora \u0026 Fungi Worldwide\u201d project, "
    "licensed CC BY-NC. https://www.inaturalist.org/projects/edible-flora-fungi-worldwide"
)

# Attribute key for attribution (present on every entity)
ATTR_ATTRIBUTION = "attribution"

# Config entry keys
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_RADIUS = "radius"
CONF_MIN_OBSERVATIONS = "min_observations"
CONF_MAX_SPECIES = "max_species"

# Defaults
DEFAULT_RADIUS = 50          # km
DEFAULT_MIN_OBSERVATIONS = 5 # minimum historical obs in this month to count as "in season"
DEFAULT_MAX_SPECIES = 30     # cap results to avoid flooding HA with entities
DEFAULT_SCAN_INTERVAL = 24   # hours between API refreshes

# Update coordinator name
COORDINATOR = "coordinator"

# Entity attribute keys
ATTR_SCIENTIFIC_NAME = "scientific_name"
ATTR_COMMON_NAME = "common_name"
ATTR_TAXON_ID = "taxon_id"
ATTR_OBSERVATION_COUNT = "observation_count"
ATTR_PHOTO_URL = "photo_url"
ATTR_WIKIPEDIA_URL = "wikipedia_url"
ATTR_INAT_URL = "inat_url"
ATTR_ICONIC_TAXON = "iconic_taxon"  # "Plantae" or "Fungi"
ATTR_MONTH = "month"
