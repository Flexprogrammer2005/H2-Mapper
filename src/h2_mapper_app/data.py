"""Loading and filtering for the source-attributed H2 Mapper site dataset."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[2]
SITES_PATH = ROOT / "data" / "derived" / "earthchem_ophiolite_screening_sites.geojson"
CATALOG_PATH = ROOT / "data" / "catalog" / "datasets.json"
CRITERIA_PATH = ROOT / "data" / "chemistry" / "generation_prerequisites.json"
COUNTRIES_PATH = ROOT / "data" / "raw" / "natural_earth" / "ne_50m_admin_0_countries.geojson"

DIRECT_CLASS = "direct_ultramafic_or_serpentinite_sample"
CONTEXT_CLASS = "ophiolite_context_sample_only"


def _flatten_feature(feature: dict[str, Any]) -> dict[str, Any]:
    properties = dict(feature["properties"])
    longitude, latitude = feature["geometry"]["coordinates"]
    properties["site_id"] = feature["id"]
    properties["longitude"] = longitude
    properties["latitude"] = latitude
    properties["evidence_label"] = (
        "Direct ultramafic / serpentinite sample"
        if properties["evidence_class"] == DIRECT_CLASS
        else "Ophiolite-context sample"
    )
    return properties


@st.cache_data(show_spinner=False)
def load_sites() -> pd.DataFrame:
    """Load the checked-in derived GeoJSON into an app-friendly data frame."""
    source = json.loads(SITES_PATH.read_text(encoding="utf-8"))
    frame = pd.DataFrame(_flatten_feature(feature) for feature in source["features"])
    return frame.sort_values("site_id").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def load_criteria() -> dict[str, Any]:
    return json.loads(CRITERIA_PATH.read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def load_country_boundaries() -> dict[str, Any]:
    """Load a local, lightweight land outline for the non-Mercator globe."""
    return json.loads(COUNTRIES_PATH.read_text(encoding="utf-8"))


def filter_sites(
    sites: pd.DataFrame,
    *,
    evidence_classes: list[str],
    reported_rocks: list[str],
    minimum_samples: int,
    search_text: str,
) -> pd.DataFrame:
    """Apply transparent client-side filters without changing the source data."""
    filtered = sites[sites["evidence_class"].isin(evidence_classes)].copy()
    filtered = filtered[filtered["sample_count"] >= minimum_samples]
    if reported_rocks:
        requested = set(reported_rocks)
        filtered = filtered[filtered["all_reported_rock_types"].apply(lambda values: bool(requested & set(values)))]
    query = search_text.strip().casefold()
    if query:
        searchable = (
            filtered["site_id"]
            + " "
            + filtered["sample_ids"].apply(" ".join)
            + " "
            + filtered["references"].apply(" ".join)
        ).str.casefold()
        filtered = filtered[searchable.str.contains(query, regex=False)]
    return filtered.reset_index(drop=True)


def site_options(sites: pd.DataFrame) -> list[tuple[str, str]]:
    return [
        (
            row.site_id,
            f"{row.site_id} · {row.latitude:.3f}, {row.longitude:.3f} · {row.evidence_label}",
        )
        for row in sites.itertuples()
    ]


def selected_site_from_event(selection: Any) -> str | None:
    """Extract the clicked feature ID from Streamlit/PyDeck selection state."""
    if not selection:
        return None
    try:
        selected = selection.get("selection", {}).get("objects", [])
        if selected:
            return selected[0].get("site_id")
    except AttributeError:
        return None
    return None

