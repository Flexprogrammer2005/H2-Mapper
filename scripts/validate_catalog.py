"""Validate source-catalog governance before any ingestion work."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from h2_mapper_dataset.catalog import CatalogValidationError, load_catalog  # noqa: E402


def main() -> int:
    catalog_path = ROOT / "data" / "catalog" / "datasets.json"
    try:
        catalog = load_catalog(catalog_path)
    except (OSError, ValueError, CatalogValidationError) as error:
        print(f"Catalog validation failed: {error}")
        return 1
    print(f"Catalog valid: {len(catalog['datasets'])} datasets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

