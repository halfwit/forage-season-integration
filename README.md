# 🍄 Forage Season — Home Assistant Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant integration that shows which edible plants and fungi are **in season near your home**, updated daily.

---

## Data & Attribution

All observation data is sourced from the iNaturalist community project:

> **[Edible Flora & Fungi Worldwide](https://www.inaturalist.org/projects/edible-flora-fungi-worldwide)**
> on [iNaturalist](https://www.inaturalist.org)

Observations © iNaturalist contributors, licensed **CC BY-NC**. This integration does not claim ownership of any data. Every sensor entity carries the project URL and attribution string in its attributes.

---

## How it works

On each daily refresh the integration calls the iNaturalist API for research-grade observations matching the current month, filtered to the `edible-flora-fungi-worldwide` project, within your configured radius. Species with enough historical observations are exposed as `sensor` entities:

- **State:** `in_season` or `out_of_season`
- **Attributes:** common name, scientific name, photo URL, iNaturalist link, Wikipedia link, observation count, taxon type (plant/fungus), data source URL

---

## Installation

### Via HACS (recommended)
1. In HACS → Integrations → ⋮ → **Custom Repositories**
2. Add this repo URL, category = **Integration**
3. Install **Forage Season**, restart Home Assistant
4. **Settings → Devices & Services → Add Integration → Forage Season**

### Manual
Copy `custom_components/forage_season/` into your `<config>/custom_components/` directory and restart.

> **Lovelace cards** are in a separate repo:
> [forage-season-card](https://github.com/halfwit/forage-season-card)

---

## Configuration

| Option | Default | Description |
|---|---|---|
| Latitude / Longitude | HA home location | Centre of the search area |
| Radius (km) | 50 | Search radius (5–500) |
| Min observations | 5 | Minimum historical obs this month to count as in-season |
| Max species | 30 | Cap on entities created |

All options are editable post-setup via **Settings → Devices & Services → Forage Season → Configure**.

---

## License & credits

- Observation data © iNaturalist contributors, CC BY-NC
- Project: [Edible Flora & Fungi Worldwide](https://www.inaturalist.org/projects/edible-flora-fungi-worldwide)
- Integration code: MIT
