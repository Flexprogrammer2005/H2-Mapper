"""Build source-attributed screening-site anchors from the EarthChem workbook.

Each output point is a unique observed sample coordinate, not a claimed
ophiolite boundary and not a hydrogen occurrence. Sites with a directly sampled
ultramafic or serpentinite rock name are explicitly distinguished from the
remaining ophiolite-context sample points.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_WORKBOOK = ROOT / "data" / "raw" / "earthchem_ophiolites" / "1307-1_Ophiolite_ALL.xlsx"
OUTPUT = ROOT / "data" / "derived" / "earthchem_ophiolite_screening_sites.geojson"
SOURCE_DATASET_ID = "earthchem_petdb_global_ophiolite_samples_2019"
SOURCE_DOI = "10.1594/IEDA/111307"
SOURCE_LICENSE = "CC-BY-SA-4.0"

# These represent direct source-rock sample classes for the initial screen.
# Other samples remain useful as ophiolite-context anchors, but are never
# silently treated as direct ultramafic evidence.
DIRECT_SOURCE_ROCKS = {
    "HARZBURGITE",
    "DUNITE",
    "LHERZOLITE",
    "SERPENTINITE",
    "PERIDOTITE",
    "METAPERIDOTITE",
    "PYROXENITE",
    "CLINOPYROXENITE",
    "ORTHOPYROXENITE",
    "WEBSTERITE",
    "WEHRLITE",
}


def stable_site_id(latitude: float, longitude: float) -> str:
    location_key = f"{latitude:.6f},{longitude:.6f}".encode("utf-8")
    return f"earthchem-ophiolite-{hashlib.sha256(location_key).hexdigest()[:12]}"


def normalise_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def build_features(data: pd.DataFrame) -> list[dict]:
    required = {"SAMPLE_ID", "LATITUDE", "LONGITUDE", "TECTONIC_SETTING", "ROCK NAME", "REFERENCE"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Workbook Data sheet is missing columns: {', '.join(sorted(missing))}")

    points = data.dropna(subset=["LATITUDE", "LONGITUDE"]).copy()
    points["LATITUDE"] = pd.to_numeric(points["LATITUDE"], errors="raise")
    points["LONGITUDE"] = pd.to_numeric(points["LONGITUDE"], errors="raise")
    points = points[
        points["LATITUDE"].between(-90, 90) & points["LONGITUDE"].between(-180, 180)
    ].copy()
    points["latitude_key"] = points["LATITUDE"].round(6)
    points["longitude_key"] = points["LONGITUDE"].round(6)

    features: list[dict] = []
    for (latitude, longitude), group in points.groupby(["latitude_key", "longitude_key"], sort=True):
        rock_types = sorted({normalise_text(value) for value in group["ROCK NAME"] if normalise_text(value)})
        references = sorted({normalise_text(value) for value in group["REFERENCE"] if normalise_text(value)})
        sample_ids = sorted({normalise_text(value) for value in group["SAMPLE_ID"] if normalise_text(value)})
        direct_rocks = sorted(set(rock_types) & DIRECT_SOURCE_ROCKS)
        evidence_class = (
            "direct_ultramafic_or_serpentinite_sample"
            if direct_rocks
            else "ophiolite_context_sample_only"
        )
        features.append(
            {
                "type": "Feature",
                "id": stable_site_id(float(latitude), float(longitude)),
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(longitude), float(latitude)],
                },
                "properties": {
                    "site_type": "ophiolite_sample_location",
                    "evidence_class": evidence_class,
                    "direct_source_rock_types": direct_rocks,
                    "all_reported_rock_types": rock_types,
                    "sample_count": int(len(group)),
                    "sample_ids": sample_ids,
                    "references": references,
                    "tectonic_setting": "OPHIOLITE",
                    "source_dataset_id": SOURCE_DATASET_ID,
                    "source_doi": SOURCE_DOI,
                    "source_license": SOURCE_LICENSE,
                    "h2_evidence_status": "not_assessed_by_this_dataset",
                    "interpretation_limit": (
                        "Point anchor only; not an ophiolite extent, an active reaction measurement, "
                        "or evidence of hydrogen occurrence or accumulation."
                    ),
                },
            }
        )
    return features


def main() -> int:
    if not RAW_WORKBOOK.exists():
        raise FileNotFoundError(f"Missing raw source workbook: {RAW_WORKBOOK}")
    data = pd.read_excel(RAW_WORKBOOK, sheet_name="Data")
    features = build_features(data)
    direct_count = sum(
        feature["properties"]["evidence_class"] == "direct_ultramafic_or_serpentinite_sample"
        for feature in features
    )
    output = {
        "type": "FeatureCollection",
        "name": "earthchem_ophiolite_screening_sites",
        "metadata": {
            "derived_dataset_version": "0.1.0",
            "source_dataset_id": SOURCE_DATASET_ID,
            "source_doi": SOURCE_DOI,
            "source_license": SOURCE_LICENSE,
            "feature_count": len(features),
            "direct_source_rock_site_count": direct_count,
            "purpose": "Global ophiolite and direct ultramafic sample-location anchors for a chemistry-led source-context screen.",
            "not_for": ["ophiolite extent", "H2 occurrence", "H2 accumulation", "resource estimate"],
        },
        "features": features,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {len(features)} unique screening sites ({direct_count} direct source-rock sites) to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

