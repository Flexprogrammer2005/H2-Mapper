import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from h2_mapper_app.data import filter_sites, load_sites


class SiteFilterTests(unittest.TestCase):
    def test_empty_result_preserves_columns_with_rock_and_text_filters(self):
        sites = load_sites()
        for query in ("", "sample"):
            with self.subTest(query=query):
                result = filter_sites(
                    sites, evidence_classes=[], reported_rocks=["DUNITE"],
                    minimum_samples=1, search_text=query,
                )
                self.assertTrue(result.empty)
                self.assertEqual(list(result.columns), list(sites.columns))
