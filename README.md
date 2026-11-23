# H2 Mapper — Source Context Explorer

**[Open the live H₂ Mapper website](https://h2-mapper-arjit.streamlit.app/)**

This folder contains an evidence-first Streamlit site and its first global,
source-attributed dataset layer. It is intentionally **not** a
hydrogen-deposit dataset or a reserve model.

## Run the site

```powershell
cd H2-Mapper
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The site includes:

- an interactive Globe.GL Earth viewer with 850 EarthChem sample sites;
- filtering by rock type, evidence class, sample count, and source identifiers;
- a selected-site evidence and provenance panel;
- downloadable filtered CSV and GeoJSON; and
- a methods/data page documenting every current claim and limitation.

## Satellite Earth view

Globe.GL uses Three.js to render a bundled Blue Marble texture (`earth.jpg`).
Rotate or zoom the globe and click a sample marker to inspect its evidence.
The globe runs without a map API key. Natural Earth boundaries supply place
labels during data preparation. A visible boundary overlay is planned.

## MongoDB evidence store

The optional MongoDB importer maintains these collections:

- `site_anchors` — the 850 source-attributed EarthChem points;
- `fault_traces` — 13,696 GEM active-fault traces;
- `hydro_context` — reserved for a selected, versioned water-access source;
- `permeability_context` — reserved for a verified GLHYMPS release; and
- `ophiolite_areas` — only independently mapped boundaries or clearly labelled
  screening envelopes, never polygons invented from points.

To run a local database with Docker Desktop:

```powershell
docker compose up -d
$env:MONGODB_URI = "mongodb://localhost:27017"
python scripts/seed_mongo.py
```

The same importer works with MongoDB Atlas by setting `MONGODB_URI` to an Atlas
connection string. The globe and Data Explorer always read the bundled site GeoJSON. The sidebar
reports database connectivity. A nearby-faults panel is planned.

## Large raw datasets

The existing GEM fault snapshot is bundled so a standard clone includes the
data needed for seeding. For future large raw files, install Git LFS and
run `git lfs track --filename "path/to/file"` before adding the file. Commit the resulting
`.gitattributes` alongside the dataset.

## Current scope

The first screen identifies broad areas where mapped geology and surface context
could be compatible with serpentinization-driven hydrogen generation. It keeps
three concepts separate:

- `source_rock_context`: mapped ultramafic, ophiolitic, peridotitic, or
  serpentinitic material;
- `surface_context`: satellite-derived land-surface information; and
- `evidence_quality`: coverage, resolution, vintage, and known limitations of
  each input.

No input may be interpreted as a measured H2 concentration, a deposit, a
resource estimate, or a discovery probability unless it is explicitly stored as
such with traceable evidence.

## First catalogued sources

The data catalog begins with USGS Landsat Collection 2, USGS-hosted SRTM
terrain, and two USGS ultramafic reference datasets. Read
`docs/dataset_scope.md` before using or adding data.

## Validate the catalog

From this directory:

```powershell
python scripts/validate_catalog.py
python -m unittest discover -s tests -v
```

## Query Landsat metadata, not imagery

The STAC helper records a small, reproducible manifest for a chosen area and
date range. It does not download raster assets or add them to source control.

```powershell
python scripts/query_usgs_landsat_stac.py `
  --bbox "-123.0,37.0,-122.0,38.0" `
  --datetime "2025-01-01/2025-12-31" `
  --output data/manifests/example.json
```

The area of interest must first be justified by mapped source-rock evidence;
Landsat is not used to infer subsurface ultramafic geology on its own.

