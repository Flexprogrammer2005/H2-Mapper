"""Minimal, dependency-free validation for the H2 Mapper dataset catalog."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ALLOWED_STATUSES = {"candidate", "approved_for_pilot", "reference_only", "rejected"}
ALLOWED_ROLES = {
    "source_rock_context",
    "source_rock_reference",
    "surface_context",
    "terrain_context",
    "fault_context",
    "water_access_context",
    "permeability_context",
    "ophiolite_boundary_reference",
    "evidence_quality",
}
REQUIRED_DATASET_FIELDS = {
    "id",
    "name",
    "provider",
    "status",
    "role",
    "geographic_coverage",
    "native_resolution",
    "access",
    "rights",
    "provenance_url",
    "permitted_use",
    "prohibited_inference",
    "known_limitations",
}


class CatalogValidationError(ValueError):
    """Raised when a source catalog cannot support traceable use."""


def load_catalog(path: Path) -> dict[str, Any]:
    """Load and validate a catalog JSON file."""
    with path.open(encoding="utf-8") as catalog_file:
        catalog = json.load(catalog_file)
    validate_catalog(catalog)
    return catalog


def validate_catalog(catalog: dict[str, Any]) -> None:
    """Reject entries that lack provenance, limitations, or a defined role."""
    if not catalog.get("catalog_version"):
        raise CatalogValidationError("catalog_version is required")
    datasets = catalog.get("datasets")
    if not isinstance(datasets, list) or not datasets:
        raise CatalogValidationError("datasets must be a non-empty list")

    seen_ids: set[str] = set()
    for dataset in datasets:
        missing = REQUIRED_DATASET_FIELDS - set(dataset)
        if missing:
            raise CatalogValidationError(
                f"{dataset.get('id', '<unknown>')} is missing: {', '.join(sorted(missing))}"
            )
        dataset_id = dataset["id"]
        if dataset_id in seen_ids:
            raise CatalogValidationError(f"Duplicate dataset id: {dataset_id}")
        seen_ids.add(dataset_id)
        if dataset["status"] not in ALLOWED_STATUSES:
            raise CatalogValidationError(f"{dataset_id} has invalid status")
        if dataset["role"] not in ALLOWED_ROLES:
            raise CatalogValidationError(f"{dataset_id} has invalid role")
        if not isinstance(dataset["known_limitations"], list) or not dataset["known_limitations"]:
            raise CatalogValidationError(f"{dataset_id} must declare known limitations")
        if not dataset["prohibited_inference"].strip():
            raise CatalogValidationError(f"{dataset_id} must declare prohibited inference")
        if not dataset["provenance_url"].startswith("https://"):
            raise CatalogValidationError(f"{dataset_id} must have an HTTPS provenance URL")

