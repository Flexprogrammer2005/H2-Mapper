# Evidence-layer plan

## MongoDB collections

| Collection | Geometry | Purpose |
| --- | --- | --- |
| `site_anchors` | Point | Source-attributed EarthChem ophiolite/ultramafic sample locations |
| `fault_traces` | LineString | GEM active-fault context, including source catalogue and available kinematic metadata |
| `hydro_context` | Point/LineString/Polygon | Selected HydroATLAS/HydroSHEDS water-access context; no groundwater claims without a suitable source |
| `permeability_context` | Polygon/Raster-derived cell | Validated GLHYMPS or equivalent broad hydrogeological context |
| `ophiolite_areas` | Polygon/MultiPolygon | Independently mapped or explicitly inferred ophiolite extent |
| `dataset_versions` | None | Immutable source file checksum, version, licence, and ingestion record |

Each spatial collection uses a MongoDB `2dsphere` index. No collection is
merged into a single untraceable score.

## Ophiolite boundaries

The current 850 EarthChem records are **points**, not boundaries. A credible
boundary must have one of these labels:

1. `mapped_boundary`: directly supplied by a licensed geological map;
2. `interpreted_boundary`: digitised or translated from a cited map, retaining
   source scale and positional uncertainty; or
3. `screening_envelope`: a clearly labelled analytical buffer/cluster around
   point evidence, never displayed as a geological boundary.

Until a polygon source is imported, the application must show site anchors only.
Generating polygons from sample points would create false precision.

## Water, faults, and permeability

- Faults are structural context; proximity does not prove permeability or H2.
- HydroATLAS can provide surface-water and catchment context, but not direct
  groundwater access or reactive water-rock contact.
- GLHYMPS can provide broad permeability context only after the chosen release,
  licence, units, and uncertainty are verified.
- Future composite screening must retain individual evidence fields and a
  separate data-quality/coverage result.

