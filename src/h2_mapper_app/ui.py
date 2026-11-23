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
            border-left: 3px solid #43897b;
            padding: .15rem 0 .2rem clamp(.85rem, 2vw, 1.5rem);
            margin-bottom: .45rem;
          }
          .atlas-header h1 { font-size: clamp(2.6rem, 5vw, 4.2rem); line-height: 1.04; padding: 0; margin: 0; }
          .atlas-header p { max-width: 66ch; margin: .5rem 0 0; color: #465d59; line-height: 1.5; }
          [data-testid="stMetric"], .st-key-site_evidence {
            background: #fff;
            border: 1px solid #d9e2dc;
            border-radius: .85rem;
          }
          [data-testid="stMetric"] { padding: .7rem 1rem; }
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
          .st-key-context_count [data-testid="stMetricLabel"]::before { background: #bc7822; }
          .st-key-site_evidence { padding: 1.1rem; gap: .55rem; }
          .st-key-site_evidence hr { margin: .35rem 0; border-color: #dde6df; }
          iframe[title$="earth_globe"] { border-radius: .85rem; }
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
        st.markdown("**Place**")
        st.write(location or "Jurisdiction unresolved at this coordinate")
        st.caption(f"{site.latitude:.5f}°, {site.longitude:.5f}° · Natural Earth land boundaries")
        st.divider()
        st.markdown("**Possibility of hydrogen generation**")
        if direct:
            rocks = ", ".join(r.lower() for r in site.direct_source_rock_types)
            st.write(f"Direct rock evidence. Samples include {rocks}. When water reaches suitable iron-bearing minerals, alteration can release hydrogen.")
        else:
            st.write("Indirect rock evidence. The samples place this site in an ophiolite, but the recorded rock types do not establish a local ultramafic source.")
        st.caption("Groundwater access, permeability and hydrogen measurements remain unverified here.")
        st.divider()
        st.markdown("**Natural hydrogen extraction rules**")
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

