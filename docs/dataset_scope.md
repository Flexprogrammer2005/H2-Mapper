# Dataset scope and scientific boundary

## Objective

Build a global, chemistry-led **possibility screen** for locations where the
prerequisites for serpentinization-driven H2 generation may co-occur. The
screen is designed for large-area discovery and transparent prioritisation.

It does not estimate reaction rate, H2 volume, commercial resource, or
probability of discovery.

## Chemistry-led minimum conditions

The relevant redox process oxidises ferrous iron in suitable primary minerals
while reducing water to H2. A simplified end-member expression is:

`3 FeO + H2O -> Fe3O4 + H2`

This is a conceptual aid, not a universal mineral-balance equation. In real
systems, mineral assemblage, alteration history, water chemistry, temperature,
permeability, and fluid pathways affect whether and how the process proceeds.

The first screen therefore uses:

1. mapped ultramafic / ophiolitic / peridotitic / serpentinitic extent as the
   source-rock prerequisite;
2. terrain and land-surface context as supporting evidence for exposure and
   water–rock-access hypotheses; and
3. explicit coverage and quality fields so data-poor areas remain distinguishable
   from areas with contrary evidence.

## Dataset handling rules

- Every dataset begins as `candidate` or `reference_only` in the catalog.
- A source may enter a derived layer only after availability, rights, coverage,
  spatial resolution, provenance, and limitations are recorded.
- Store acquisition time, source URL, dataset version, quality-mask use, and
  processing parameters for every derived output.
- Do not ingest global raster imagery into MongoDB. Store its catalog metadata,
  footprints, and derivative provenance; retain raster assets externally only
  when a selected area of interest requires them.
- Do not infer an H2 occurrence, deposit, or accumulation from satellite,
  terrain, proximity, or lithology data.

## Initial data roles

| Role | Inputs | Permitted interpretation |
| --- | --- | --- |
| Source-rock context | Geologic maps and vetted ultramafic references | Mapped candidate host/source-rock extent |
| Surface context | Landsat Collection 2 surface reflectance/temperature | Surface conditions and quality-masked interpretation |
| Terrain context | SRTM | Drainage, slope, accessibility, and terrain context |
| Evidence quality | Catalog metadata and QA bands | Confidence in the input, not prospectivity |

## Status definitions

- `candidate`: catalogued, but not yet approved for automated processing.
- `approved_for_pilot`: fit for a stated pilot use only.
- `reference_only`: useful for discovery or comparison; not a production layer.
- `rejected`: cannot be used under the recorded conditions.

