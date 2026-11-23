"""Shared Streamlit display components."""

from __future__ import annotations

import streamlit as st

import json
from functools import lru_cache

from h2_mapper_app.data import DIRECT_CLASS, ROOT


@lru_cache(maxsize=1)
def _site_context():
    data = ROOT / "data"
    places = json.loads((data / "derived/site_places.json").read_text(encoding="utf-8"))
    policy = json.loads((data / "catalog/extraction_rules.json").read_text(encoding="utf-8"))
    return places, policy


def inject_theme() -> None:
    st.html(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@500&display=swap');
          .atlas-header small { display:block; margin-top:.6rem; color:#a8dfcd; font-weight:600; letter-spacing:.025em; }
          .map-step span { display:inline-grid; place-items:center; width:1.55rem; height:1.55rem; border-radius:50%; background:#196c60; color:white; margin-right:.55rem; }
          .map-step p { margin:.55rem 0; }
          .evidence-chip { display:inline-block; padding:.18rem .65rem; border-radius:1rem; font-size:.86rem; font-weight:650; }
          .place { background:#e6eef1; color:#284c61; }
          .chemistry { background:#deeee6; color:#225749; }
          .rules { background:#f6ecd8; color:#684a17; }
          [data-testid="stMainBlockContainer"] {
            max-width: 96rem;
            padding-top: 4.25rem;
          }
          [data-testid="stMain"] h1 {
            font-family: "Source Serif 4", Georgia, serif;
            font-weight: 500;
            letter-spacing: -.045em;
          }
          header.atlas-header {
            background:
              linear-gradient(90deg, #123831 12%, #123831eb 52%, transparent 90%),
              repeating-radial-gradient(ellipse at 108% 120%, transparent 0 21px,
                #b3e5d027 22px, transparent 24px 34px),
              linear-gradient(115deg, #123831, #28594d);
            border-radius: 1rem;
            padding: clamp(1rem, 2.2vw, 1.75rem);
            margin-bottom: .45rem;
          }
          .atlas-header h1 { color:#fffaf0; font-size: clamp(2.6rem, 5vw, 4.2rem); line-height: 1.04; padding: 0; margin: 0; }
          .atlas-header p { max-width: 66ch; margin: .5rem 0 0; color: #e0ede6; line-height: 1.5; }
          [data-testid="stMetric"], .st-key-site_evidence {
            background: #fff;
            border: 1px solid #d9e2dc;
            border-radius: .85rem;
          }
          [data-testid="stMetric"] { padding: .7rem 1rem; box-shadow:0 2px 7px #17372b08; }
          [data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; line-height: 1.2; }
          .st-key-direct_count [data-testid="stMetricLabel"]::before,
          .st-key-context_count [data-testid="stMetricLabel"]::before {
            content: "";
            width: .55rem;
            height: .55rem;
            flex: 0 0 auto;
            align-self: center;
            margin-right: .25rem;
            border-radius: 50%;
            background: #148571;
          }
          .st-key-context_count [data-testid="stMetricLabel"]::before { background: #bc7822; border-radius: 0; transform: rotate(45deg); }
          .st-key-site_evidence { padding: 1.1rem; gap: .55rem; }
          .st-key-site_evidence hr { margin: .35rem 0; border-color: #dde6df; }
          iframe[title$="earth_globe"] { box-sizing:border-box; border:1px solid #385650; box-shadow:0 0 0 3px #e0e9e2, 0 8px 24px #13352d18; border-radius: 1rem; }
          @media (max-width: 640px) {
            [data-testid="stMainBlockContainer"] { padding-top: 3.75rem; }
            .st-key-site_counts [data-testid="stHorizontalBlock"] {
              display: grid;
              grid-template-columns: repeat(3, minmax(0, 1fr));
              gap: .35rem;
            }
            .st-key-site_counts [data-testid="stColumn"] { min-width: 0; width: 100%; }
            [data-testid="stMetric"] { padding: .5rem; }
            [data-testid="stMetricLabel"] { min-height: 2.5rem; }
            [data-testid="stMetricLabel"] p { font-size: .8rem; white-space: normal; line-height: 1.2; }
            [data-testid="stMetricValue"] { font-size: 1.5rem; }
          }
        </style>
        """,
    )


def render_site_evidence(site: object) -> None:
    direct = site.evidence_class == DIRECT_CLASS
    places, policy = _site_context()
    place = places.get(site.site_id, {})
    country = place.get("country", "")
    region = place.get("region", "")
    code = place.get("code", "")
    location = ", ".join(dict.fromkeys(x for x in (region, country) if x))
    with st.container(key="site_evidence"):
        st.html('<span class="evidence-chip place">Place</span>')
        st.write(location or "Jurisdiction unresolved at this coordinate")
        st.caption(f"{site.latitude:.5f}°, {site.longitude:.5f}° · Natural Earth land boundaries")
        st.divider()
        st.html('<span class="evidence-chip chemistry">Possibility of hydrogen generation</span>')
        if direct:
            rocks = ", ".join(r.lower() for r in site.direct_source_rock_types)
            st.write(f"Direct rock evidence. Samples include {rocks}. When water reaches suitable iron-bearing minerals, alteration can release hydrogen.")
        else:
            st.write("Indirect rock evidence. The samples place this site in an ophiolite, but the recorded rock types do not establish a local ultramafic source.")
        st.caption("Groundwater access, permeability and hydrogen measurements remain unverified here.")
        st.divider()
        st.html('<span class="evidence-chip rules">Natural hydrogen extraction rules</span>')
        rules = policy["rules"]
        rule = rules.get(f"{code}/{region}") or rules.get(code)
        if rule:
            status, note, source, url = rule
            st.write(status)
            st.write(note)
            st.caption(f"[{source}]({url}) · Reviewed {policy['reviewed']}")
        elif country:
            st.write(f"Unverified. A natural hydrogen production route for {location} has yet to be documented in this map.")
        else:
            st.write("Unassessed. The land boundaries do not resolve the governing jurisdiction for this point.")
    with st.expander("Samples and sources"):
        st.write(f"{site.sample_count} sample records · " + ", ".join(site.all_reported_rock_types))
        st.caption("Sample IDs")
        st.code("\n".join(site.sample_ids) or "No sample ID supplied")
        st.caption("References")
        st.write("; ".join(site.references) or "No reference supplied")
        st.caption("Interpretation limit")
        st.write(site.interpretation_limit)
        st.caption(f"Source DOI: {site.source_doi} · Licence: {site.source_license}")

