"""Methods, data provenance, and non-claims for H2 Mapper."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from h2_mapper_app.data import load_catalog, load_criteria  # noqa: E402
from h2_mapper_app.ui import inject_theme  # noqa: E402


st.set_page_config(page_title="H₂ Mapper | Methods", page_icon="◈", layout="wide")
inject_theme()
criteria = load_criteria()
catalog = load_catalog()

st.title("Methods and data")
st.markdown(
    "The current product is a transparent **source-context** screen. It identifies mapped "
    "conditions that could be compatible with serpentinization-driven H₂ generation."
)

st.subheader("What the model does not claim")
st.warning(
    "It does not estimate reaction rate, hydrogen volume, commercial resource, discovery probability, "
    "or accumulation prospectivity. Source potential and accumulation are separate questions.",
    icon="⚠️",
)

st.subheader("Generation prerequisites")
for criterion in criteria["criteria"]:
    with st.expander(criterion["question"], expanded=criterion["classification"] == "required"):
        st.caption(criterion["classification"].replace("_", " ").upper())
        st.write("**Acceptable evidence:** " + "; ".join(criterion["acceptable_evidence"]))
        st.write("**Guardrail:** " + criterion["forbidden_shortcut"])

st.subheader("Catalogued data sources")
for dataset in catalog["datasets"]:
    with st.expander(f"{dataset['name']} — {dataset['status'].replace('_', ' ')}"):
        col_a, col_b = st.columns(2)
        col_a.write(f"**Role:** {dataset['role'].replace('_', ' ')}")
        col_a.write(f"**Coverage:** {dataset['geographic_coverage']}")
        col_a.write(f"**Resolution:** {dataset['native_resolution']}")
        col_b.write(f"**Rights:** {dataset['rights']['status']}")
        col_b.markdown(f"[Source / provenance]({dataset['provenance_url']})")
        st.write("**Permitted interpretation:** " + dataset["permitted_use"])
        st.write("**Not permitted:** " + dataset["prohibited_inference"])
        st.write("**Known limitations:** " + " ".join(dataset["known_limitations"]))

st.subheader("Planned evidence collections")
st.markdown(
    "MongoDB stores `site_anchors`, `fault_traces`, `hydro_context`, "
    "`permeability_context`, `ophiolite_areas`, and `dataset_versions` separately. "
    "This prevents a fault or river layer from being mistaken for proof of H₂."
)
st.caption("Boundary labels and collection roles are documented in `docs/model_layers.md`.")

