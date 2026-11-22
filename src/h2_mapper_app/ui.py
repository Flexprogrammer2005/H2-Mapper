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
    st.markdown(
        """
        <style>
          .stApp { background: #f6f8fb; color: #10202f; }
          h1 { letter-spacing: -0.045em; font-weight: 750; }
          .eyebrow { color: #0d8b7c; font-weight: 700; font-size: 0.78rem; letter-spacing: 0.12em; margin-bottom: -0.55rem; }
          [data-testid="stMetric"] { background: white; border: 1px solid #e3e9ee; border-radius: 12px; padding: 0.8rem; }
          .evidence-card { background: white; border: 1px solid #e3e9ee; border-radius: 14px; padding: 1.1rem; }
          .tag { display: inline-block; padding: 0.2rem 0.5rem; border-radius: 99px; margin: 0.1rem 0.15rem 0.1rem 0; font-size: 0.78rem; background: #e6f6f3; color: #076c61; }
          .tag-muted { background: #fff0d7; color: #8a5500; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_site_evidence(site: object) -> None:
    direct = site.evidence_class == DIRECT_CLASS
    places, policy = _site_context()
    place = places.get(site.site_id, {})
    country = place.get("country", "")
    region = place.get("region", "")
    code = place.get("code", "")
    location = ", ".join(dict.fromkeys(x for x in (region, country) if x))
    with st.container(border=True):
        st.markdown("**Place**")
        st.write(location or "Jurisdiction unresolved at this coordinate")
        st.caption(f"{site.latitude:.5f}°, {site.longitude:.5f}° · Natural Earth land boundaries")
        st.markdown("**Possibility of hydrogen generation**")
        if direct:
            rocks = ", ".join(r.lower() for r in site.direct_source_rock_types)
            st.write(f"Direct rock evidence. Samples include {rocks}. When water reaches suitable iron-bearing minerals, alteration can release hydrogen.")
        else:
            st.write("Indirect rock evidence. The samples place this site in an ophiolite, but the recorded rock types do not establish a local ultramafic source.")
        st.caption("Groundwater access, permeability and hydrogen measurements remain unverified here.")
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

