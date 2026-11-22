from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from h2_mapper_dataset.catalog import CatalogValidationError, load_catalog, validate_catalog


class CatalogTests(unittest.TestCase):
    def test_checked_in_catalog_is_valid(self) -> None:
        catalog = load_catalog(ROOT / "data" / "catalog" / "datasets.json")
        self.assertGreaterEqual(len(catalog["datasets"]), 4)

    def test_missing_prohibited_inference_is_rejected(self) -> None:
        catalog = json.loads((ROOT / "data" / "catalog" / "datasets.json").read_text())
        catalog["datasets"][0]["prohibited_inference"] = ""
        with self.assertRaises(CatalogValidationError):
            validate_catalog(catalog)

    def test_duplicate_ids_are_rejected(self) -> None:
        catalog = json.loads((ROOT / "data" / "catalog" / "datasets.json").read_text())
        catalog["datasets"][1]["id"] = catalog["datasets"][0]["id"]
        with self.assertRaises(CatalogValidationError):
            validate_catalog(catalog)


if __name__ == "__main__":
    unittest.main()

