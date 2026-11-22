"""Save a reproducible USGS Landsat STAC metadata manifest for a chosen AOI.

The script deliberately saves STAC metadata only. It never downloads imagery;
raster acquisition belongs to an approved, area-specific processing run.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


STAC_SEARCH_URL = "https://landsatlook.usgs.gov/stac-server/search"
VALID_COLLECTIONS = {"landsat-c2l2-sr", "landsat-c2l2-st"}


def parse_bbox(value: str) -> list[float]:
    try:
        bbox = [float(part) for part in value.split(",")]
    except ValueError as error:
        raise argparse.ArgumentTypeError("bbox values must be numbers") from error
    if len(bbox) != 4:
        raise argparse.ArgumentTypeError("bbox must be min_lon,min_lat,max_lon,max_lat")
    min_lon, min_lat, max_lon, max_lat = bbox
    if not (-180 <= min_lon < max_lon <= 180 and -90 <= min_lat < max_lat <= 90):
        raise argparse.ArgumentTypeError("bbox is outside WGS84 bounds or is inverted")
    return bbox


def query_stac(collection: str, bbox: list[float], datetime_range: str, limit: int) -> dict:
    payload = json.dumps(
        {
            "collections": [collection],
            "bbox": bbox,
            "datetime": datetime_range,
            "limit": limit,
        }
    ).encode("utf-8")
    request = Request(
        STAC_SEARCH_URL,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/geo+json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError(f"USGS STAC query failed: {error}") from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bbox", required=True, type=parse_bbox)
    parser.add_argument("--datetime", required=True, dest="datetime_range")
    parser.add_argument("--collection", choices=sorted(VALID_COLLECTIONS), default="landsat-c2l2-sr")
    parser.add_argument("--limit", type=int, default=10, choices=range(1, 101))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    features = query_stac(args.collection, args.bbox, args.datetime_range, args.limit)
    manifest = {
        "manifest_version": "0.1.0",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source": "USGS LandsatLook STAC Server",
        "search_url": STAC_SEARCH_URL,
        "query": {
            "collection": args.collection,
            "bbox": args.bbox,
            "datetime": args.datetime_range,
            "limit": args.limit,
        },
        "result": features,
        "notice": "Metadata manifest only. No imagery was downloaded by this script.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Saved {len(features.get('features', []))} STAC records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

