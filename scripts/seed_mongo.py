"""Load source-attributed H2 Mapper layers into MongoDB.

Usage:
    $env:MONGODB_URI='mongodb://localhost:27017'
    python scripts/seed_mongo.py

The importer creates independent collections for site anchors, fault traces,
hydro context, permeability context, and ophiolite areas. It does not invent
boundaries or water/permeability values when those source datasets are absent.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from pymongo import UpdateOne

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from h2_mapper_app.mongo import ensure_indexes, get_database  # noqa: E402


SITES_PATH = ROOT / "data" / "derived" / "earthchem_ophiolite_screening_sites.geojson"
FAULTS_PATH = ROOT / "data" / "raw" / "gem_active_faults" / "gem_active_faults_harmonized.geojson"
CATALOG_PATH = ROOT / "data" / "catalog" / "datasets.json"


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_geojson(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def upsert_features(database, collection_name: str, dataset_version_id: str, source: dict, features: list[dict]) -> int:
    operations = []
    for ordinal, feature in enumerate(features):
        feature_id = str(feature.get("id") or feature["properties"].get("catalog_id") or ordinal)
        document = {
            "_id": f"{dataset_version_id}:{feature_id}",
            "dataset_version_id": dataset_version_id,
            "source": source,
            "geometry": feature["geometry"],
            "properties": feature.get("properties", {}),
            "ingested_at": datetime.now(timezone.utc),
        }
        operations.append(UpdateOne({"_id": document["_id"]}, {"$set": document}, upsert=True))
    if operations:
        database[collection_name].bulk_write(operations, ordered=False)
    return len(operations)


def main() -> int:
    database = get_database()
    ensure_indexes(database)
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    datasets = {dataset["id"]: dataset for dataset in catalog["datasets"]}
    imported_at = datetime.now(timezone.utc)

    site_geojson = load_geojson(SITES_PATH)
    site_version = "earthchem_petdb_global_ophiolite_samples_2019:derived-0.1.0"
    database.dataset_versions.update_one(
        {"dataset_id": "earthchem_petdb_global_ophiolite_samples_2019", "version_label": "derived-0.1.0"},
        {
            "$set": {
                "dataset_id": "earthchem_petdb_global_ophiolite_samples_2019",
                "version_label": "derived-0.1.0",
                "source_file": str(SITES_PATH.name),
                "checksum_sha256": checksum(SITES_PATH),
                "source_metadata": datasets["earthchem_petdb_global_ophiolite_samples_2019"],
                "ingested_at": imported_at,
            }
        },
        upsert=True,
    )
    site_count = upsert_features(
        database,
        "site_anchors",
        site_version,
        {"dataset_id": "earthchem_petdb_global_ophiolite_samples_2019"},
        site_geojson["features"],
    )

    fault_geojson = load_geojson(FAULTS_PATH)
    fault_version = "gem_global_active_faults_v2020:harmonized-snapshot"
    database.dataset_versions.update_one(
        {"dataset_id": "gem_global_active_faults_v2020", "version_label": "harmonized-snapshot"},
        {
            "$set": {
                "dataset_id": "gem_global_active_faults_v2020",
                "version_label": "harmonized-snapshot",
                "source_file": str(FAULTS_PATH.name),
                "checksum_sha256": checksum(FAULTS_PATH),
                "source_metadata": datasets["gem_global_active_faults_v2020"],
                "ingested_at": imported_at,
            }
        },
        upsert=True,
    )
    fault_count = upsert_features(
        database,
        "fault_traces",
        fault_version,
        {"dataset_id": "gem_global_active_faults_v2020"},
        fault_geojson["features"],
    )

    print(f"MongoDB seeded: {site_count} site anchors and {fault_count} fault traces.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

