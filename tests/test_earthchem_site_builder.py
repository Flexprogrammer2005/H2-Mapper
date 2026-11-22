from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_earthchem_ophiolite_sites import DIRECT_SOURCE_ROCKS, build_features


class EarthChemSiteBuilderTests(unittest.TestCase):
    def test_derived_output_has_at_least_500_real_coordinate_sites(self) -> None:
        output = ROOT / "data" / "derived" / "earthchem_ophiolite_screening_sites.geojson"
        dataset = json.loads(output.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(dataset["features"]), 500)
        self.assertEqual(dataset["metadata"]["feature_count"], len(dataset["features"]))

    def test_direct_source_rock_class_is_not_assigned_to_basalt_only_site(self) -> None:
        import pandas as pd

        points = pd.DataFrame(
            [
                {"SAMPLE_ID": "a", "LATITUDE": 10, "LONGITUDE": 20, "TECTONIC_SETTING": "OPHIOLITE", "ROCK NAME": "BASALT", "REFERENCE": "r"},
                {"SAMPLE_ID": "b", "LATITUDE": 11, "LONGITUDE": 21, "TECTONIC_SETTING": "OPHIOLITE", "ROCK NAME": "DUNITE", "REFERENCE": "r"},
            ]
        )
        features = build_features(points)
        classes = {feature["properties"]["all_reported_rock_types"][0]: feature["properties"]["evidence_class"] for feature in features}
        self.assertEqual(classes["BASALT"], "ophiolite_context_sample_only")
        self.assertEqual(classes["DUNITE"], "direct_ultramafic_or_serpentinite_sample")
        self.assertIn("DUNITE", DIRECT_SOURCE_ROCKS)


if __name__ == "__main__":
    unittest.main()

