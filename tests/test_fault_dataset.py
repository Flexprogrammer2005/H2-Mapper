from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FAULTS_PATH = ROOT / "data" / "raw" / "gem_active_faults" / "gem_active_faults_harmonized.geojson"


class FaultDatasetTests(unittest.TestCase):
    def test_fault_snapshot_is_nonempty_and_geospatial(self) -> None:
        faults = json.loads(FAULTS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(faults["type"], "FeatureCollection")
        self.assertGreaterEqual(len(faults["features"]), 10_000)
        self.assertTrue(all(feature["geometry"]["type"] == "LineString" for feature in faults["features"]))
        self.assertTrue(all("catalog_id" in feature["properties"] for feature in faults["features"]))


if __name__ == "__main__":
    unittest.main()

