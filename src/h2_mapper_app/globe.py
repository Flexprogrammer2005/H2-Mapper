"""Locally served Globe.GL map for the Streamlit site explorer."""

from pathlib import Path

import pandas as pd
import streamlit.components.v1 as components

from h2_mapper_app.data import DIRECT_CLASS

_globe = components.declare_component(
    "earth_globe", path=str(Path(__file__).with_name("earth_globe"))
)


def render_satellite_globe(sites: pd.DataFrame):
    """Send filtered coordinates and receive the most recent marker click."""
    columns = ["site_id", "latitude", "longitude", "evidence_class"]
    return _globe(
        sites=sites[columns].to_dict(orient="records"),
        direct_class=DIRECT_CLASS,
        key="site_globe",
        default=None,
    )
