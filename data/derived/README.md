# Derived screening-site dataset

`earthchem_ophiolite_screening_sites.geojson` is the first actual spatial input
to the H2 Mapper source-context model.

## Contents

- **850** unique, source-attributed global coordinate sites.
- **431** sites include at least one directly sampled ultramafic or
  serpentinite rock type: harzburgite, dunite, lherzolite, serpentinite,
  peridotite, metaperidotite, pyroxenite, clinopyroxenite, orthopyroxenite,
  websterite, or wehrlite.
- The remaining sites are retained as `ophiolite_context_sample_only`; they
  must never be silently upgraded to direct ultramafic evidence.

## Provenance

- Input: `data/raw/earthchem_ophiolites/1307-1_Ophiolite_ALL.xlsx`
- Input SHA-256:
  `F07EA0E3B2E7576B2C361ECD1EE50D2D0475838DB674712D9E7548C296112127`
- Source: PetDB Team (2019), *EarthChem Data-To-Go: Geochemical Data for
  Ophiolites, version February 2019*, DOI: 10.1594/IEDA/111307
- Licence: CC BY-SA 4.0
- Builder: `scripts/build_earthchem_ophiolite_sites.py`

## Interpretation boundary

This is a set of real sample-location anchors, not polygons of ophiolite
extent. It provides a minimum global inventory for the first chemistry-led
screen and is intended to be overlaid with independent geology, water-access,
and satellite-context layers. It does not contain H2 measurements and cannot
identify an H2 deposit or accumulation.

