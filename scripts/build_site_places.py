"""Build offline place labels. Pass the Natural Earth v5.1.2 Admin 1 GeoJSON.

Source: https://github.com/nvkelso/natural-earth-vector/blob/v5.1.2/geojson/ne_10m_admin_1_states_provinces.geojson
Requires Shapely 2 for rebuilding only.
"""
import json
import sys
from pathlib import Path

from shapely.geometry import shape
from shapely.strtree import STRtree

DATA = Path(__file__).resolve().parents[1] / "data"


def layer(path):
    features = json.loads(path.read_text(encoding="utf-8"))["features"]
    return STRtree([shape(f["geometry"]) for f in features]), [f["properties"] for f in features]


def matches(layer_data, point):
    tree, attributes = layer_data
    return [attributes[i] for i in tree.query(point, predicate="intersects")]


def main(region_file):
    countries = layer(DATA / "raw/natural_earth/ne_50m_admin_0_countries.geojson")
    regions = layer(region_file)
    sites = json.loads((DATA / "derived/earthchem_ophiolite_screening_sites.geojson").read_text(encoding="utf-8"))
    places = {}
    for site in sites["features"]:
        point = shape(site["geometry"])
        country_hits = matches(countries, point)
        region_hits = matches(regions, point)
        names = {p["ADM0_A3"]: p["ADMIN"] for p in country_hits}
        for p in region_hits:
            names.setdefault(p["adm0_a3"], p["admin"])
        code, country = next(iter(names.items())) if len(names) == 1 else ("", "")
        region = ""
        if code and len(region_hits) == 1:
            region = region_hits[0]["name_en"] or region_hits[0]["name"] or ""
        places[site["id"]] = dict(code=code, country=country, region=region)
    output = DATA / "derived/site_places.json"
    output.write_text(json.dumps(places, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
