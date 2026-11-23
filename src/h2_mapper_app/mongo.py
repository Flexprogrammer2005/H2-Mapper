"""MongoDB setup and geospatial repositories for H2 Mapper evidence layers."""

from __future__ import annotations

import os
from typing import Any

from pymongo import ASCENDING, GEOSPHERE, MongoClient
from pymongo.database import Database


DEFAULT_DATABASE = "h2_mapper"


def configured_uri() -> str | None:
    """Return the optional MongoDB URI without ever exposing it in the UI."""
    return os.getenv("MONGODB_URI")


def get_database(uri: str | None = None, database_name: str | None = None) -> Database:
    connection_uri = uri or configured_uri()
    if not connection_uri:
        raise RuntimeError("MongoDB is not configured. Set MONGODB_URI in your environment.")
    client = MongoClient(connection_uri, serverSelectionTimeoutMS=5_000, appname="h2-mapper")
    return client[database_name or os.getenv("MONGODB_DATABASE", DEFAULT_DATABASE)]


def ensure_indexes(database: Database) -> None:
    """Create the indexes needed for source-specific spatial evidence queries."""
    database.site_anchors.create_index([("geometry", GEOSPHERE)], name="site_anchor_geometry")
    database.site_anchors.create_index(
        [("dataset_version_id", ASCENDING), ("properties.evidence_class", ASCENDING)],
        name="site_anchor_evidence",
    )
    database.fault_traces.create_index([("geometry", GEOSPHERE)], name="fault_geometry")
    database.fault_traces.create_index(
        [("dataset_version_id", ASCENDING), ("properties.catalog_id", ASCENDING)],
        name="fault_catalog",
    )
    database.ophiolite_areas.create_index([("geometry", GEOSPHERE)], name="ophiolite_area_geometry")
    database.hydro_context.create_index([("geometry", GEOSPHERE)], name="hydro_context_geometry")
    database.permeability_context.create_index([("geometry", GEOSPHERE)], name="permeability_context_geometry")
    database.dataset_versions.create_index(
        [("dataset_id", ASCENDING), ("version_label", ASCENDING)], unique=True, name="dataset_version_unique"
    )


def connection_status() -> tuple[bool, str]:
    """Give the UI a short status while remaining usable without MongoDB."""
    if not configured_uri():
        return False, "GeoJSON mode — set MONGODB_URI to activate the shared evidence database."
    try:
        get_database().command("ping")
    except Exception:
        return False, "MongoDB URI is configured but the database is unreachable."
    return True, "MongoDB connected — shared evidence database active."


def nearest_faults(database: Database, point: dict[str, Any], max_distance_m: int = 100_000, limit: int = 10) -> list[dict[str, Any]]:
    """Planned site evidence panel query. No page currently calls it."""
    return list(
        database.fault_traces.find(
            {
                "geometry": {
                    "$near": {
                        "$geometry": point,
                        "$maxDistance": max_distance_m,
                    }
                }
            },
            {"geometry": 0},
        ).limit(limit)
    )

