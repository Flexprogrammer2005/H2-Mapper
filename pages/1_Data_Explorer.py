"""Downloadable evidence-table view for the H2 Mapper site inventory."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from h2_mapper_app.data import CONTEXT_CLASS, DIRECT_CLASS, filter_sites, load_sites  # noqa: E402
from h2_mapper_app.ui import inject_theme  # noqa: E402


st.set_page_config(page_title="H₂ Mapper | Data Explorer", page_icon="◈", layout="wide")
inject_theme()
st.title("Data explorer")
st.markdown("Inspect and export the source-attributed screening-site inventory.")

sites = load_sites()
left, right = st.columns(2)
with left:
    classes = st.multiselect(
        "Evidence class",
        [DIRECT_CLASS, CONTEXT_CLASS],
        default=[DIRECT_CLASS, CONTEXT_CLASS],
    )
    search = st.text_input("Search site ID, sample ID, or reference")
with right:
    rocks = sorted({rock for values in sites["all_reported_rock_types"] for rock in values})
    selected_rocks = st.multiselect("Reported rock type", rocks)
    min_samples = st.number_input("Minimum samples at coordinate", min_value=1, max_value=100, value=1)

filtered = filter_sites(
    sites,
    evidence_classes=classes,
    reported_rocks=selected_rocks,
    minimum_samples=int(min_samples),
    search_text=search,
)

st.caption(f"{len(filtered):,} of {len(sites):,} source-attributed sites shown.")
table = filtered[
    [
        "site_id",
        "evidence_label",
        "latitude",
        "longitude",
        "sample_count",
        "all_reported_rock_types",
        "sample_ids",
        "references",
        "source_doi",
        "source_license",
    ]
]
st.dataframe(table, hide_index=True, width="stretch", height=520)

csv = table.assign(
    all_reported_rock_types=table["all_reported_rock_types"].apply("; ".join),
    sample_ids=table["sample_ids"].apply("; ".join),
    references=table["references"].apply("; ".join),
).to_csv(index=False).encode("utf-8")
st.download_button("Download filtered CSV", csv, "h2_mapper_screening_sites.csv", "text/csv")

geojson_features = []
for row in filtered.itertuples():
    properties = {
        "site_id": row.site_id,
        "evidence_class": row.evidence_class,
        "evidence_label": row.evidence_label,
        "sample_count": row.sample_count,
        "all_reported_rock_types": row.all_reported_rock_types,
        "sample_ids": row.sample_ids,
        "references": row.references,
        "source_doi": row.source_doi,
        "source_license": row.source_license,
        "h2_evidence_status": row.h2_evidence_status,
        "interpretation_limit": row.interpretation_limit,
    }
    geojson_features.append(
        {"type": "Feature", "id": row.site_id, "geometry": {"type": "Point", "coordinates": [row.longitude, row.latitude]}, "properties": properties}
    )
geojson = json.dumps({"type": "FeatureCollection", "features": geojson_features}, indent=2).encode("utf-8")
st.download_button("Download filtered GeoJSON", geojson, "h2_mapper_screening_sites.geojson", "application/geo+json")

