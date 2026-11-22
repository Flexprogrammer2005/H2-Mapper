"""H2 Mapper: a chemistry-led global source-context explorer."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from h2_mapper_app.data import (  # noqa: E402
    DIRECT_CLASS,
    CONTEXT_CLASS,
    filter_sites,
    load_sites,
    site_options,
)
from h2_mapper_app.mongo import connection_status  # noqa: E402
from h2_mapper_app.globe import render_satellite_globe  # noqa: E402
from h2_mapper_app.ui import inject_theme, render_site_evidence  # noqa: E402


st.set_page_config(
    page_title="H₂ Mapper | Source Context",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()

sites = load_sites()

st.markdown("<p class='eyebrow'>CHEMISTRY-LED GLOBAL SCREENING</p>", unsafe_allow_html=True)
st.title("H₂ Mapper")
st.markdown(
    "**Map where the surface geology contains source-rock context compatible with "
    "possible serpentinization-driven hydrogen generation.**"
)
st.info(
    "This is a source-context screen, not a hydrogen-deposit, reserve, reaction-rate, "
    "or discovery-probability map.",
    icon="ℹ️",
)

with st.sidebar:
    st.header("Screening controls")
    mongo_connected, mongo_message = connection_status()
    st.caption("● " + mongo_message)
    evidence_labels = st.multiselect(
        "Evidence class",
        options=[DIRECT_CLASS, CONTEXT_CLASS],
        default=[DIRECT_CLASS, CONTEXT_CLASS],
        format_func=lambda value: {
            DIRECT_CLASS: "Direct ultramafic / serpentinite sample",
            CONTEXT_CLASS: "Ophiolite-context sample",
        }[value],
    )
    rock_options = sorted({rock for rocks in sites["all_reported_rock_types"] for rock in rocks})
    selected_rocks = st.multiselect("Reported rock type", options=rock_options)
    minimum_samples = st.slider("Minimum samples at a coordinate", min_value=1, max_value=25, value=1)
    search = st.text_input("Search sample ID, reference, or site ID")
    st.divider()
    st.caption("A site is a real geochemical sample coordinate. It is not a mapped ophiolite boundary.")

filtered = filter_sites(
    sites,
    evidence_classes=evidence_labels,
    reported_rocks=selected_rocks,
    minimum_samples=minimum_samples,
    search_text=search,
)

direct_count = int((filtered["evidence_class"] == DIRECT_CLASS).sum())
context_count = int((filtered["evidence_class"] == CONTEXT_CLASS).sum())
metric_a, metric_b, metric_c = st.columns(3)
metric_a.metric("Mapped screening sites", f"{len(filtered):,}")
metric_b.metric("Direct source-rock anchors", f"{direct_count:,}")
metric_c.metric("Ophiolite-context anchors", f"{context_count:,}")

if filtered.empty:
    st.warning("No sites match the current filters. Broaden a filter to restore map results.")
    st.stop()

map_column, evidence_column = st.columns([1.8, 1], gap="large")
with map_column:
    st.subheader("Satellite Earth source-rock explorer")
    st.caption("Drag to rotate, scroll to zoom, and click a marker to select its site.")
    click = render_satellite_globe(filtered)

with evidence_column:
    st.subheader("Selected-site evidence")
    options = site_options(filtered)
    if click and click != st.session_state.get("handled_globe_click"):
        st.session_state.handled_globe_click = click
        match = next((item for item in options if item[0] == click["site_id"]), None)
        if match:
            st.session_state.evidence_site = match
    selected_site_id = st.selectbox(
        "Choose a site",
        options=options,
        key="evidence_site",
        format_func=lambda option: option[1],
        label_visibility="collapsed",
    )[0]
    selected = filtered.loc[filtered["site_id"] == selected_site_id]
    if selected.empty:
        selected = filtered.iloc[[0]]
    render_site_evidence(selected.iloc[0])

st.divider()
st.markdown("### How to read this map")
left, middle, right = st.columns(3)
left.markdown("**1. Source rock**  \nDirect rock samples carry stronger source-rock evidence than ophiolite context alone.")
middle.markdown("**2. Conditions still required**  \nWater access, alteration, permeability, and temperature require independent layers.")
right.markdown("**3. Accumulation stays separate**  \nThis map says nothing about traps, seals, migration, preservation, or commercial volumes.")

