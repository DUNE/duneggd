[GeGeDe](https://github.com/brettviren/gegede)-based geometry builder for the DUNE Far Detector-Vertical Drift

- First install GeGeDe by following the instructions in the link above

- Then, one can generate output gdml by running :
```
gegede-cli dunevd_v8.cfg -o dunevd10kt_v8_full10kt_support_cavern.gdml
```

May have to add current directory to `PYTHONPATH` before doing so with :

```
export PYTHONPATH=`pwd`:$PYTHONPATH
```

The file : `dunevd_v8.cfg` stores the configuration parameters and builder hierarchy. It uses defaults from `utils/globals.py`.
Currently default configuration is to construct the full 10kt VD geometry along with the cavern hall, current support structure design and other details (see below image).

<img width="1916" height="1077" alt="Screen Shot 2025-12-18 at 19 10 08" src="https://github.com/user-attachments/assets/25448fae-a2fc-442b-8fac-b704d3905e5d" />

Apply `simple=True` and the appropriate `workspace` option within it to default back to the simplified "workspace"-type geometries that many simulations use. For example :
```
workspace = 1 and simple = True : 1x8x14
workspace = 4 and simple = True : 2x8x40
```

For visualization, one can refer to `gl.C` or `geoDisplay.C` (former having more flexibility in turning on-off certain volumes)
For checking overlaps, one can run `check_overlap.C`

X-Arapuca mesh structures (lateral membrane mesh, cathode-side conductive mesh, cathode resistive mesh) ported from `generate_protodunevd_v5_refactored.pl` are off by default. Set `ArapucaMesh_switch = True` in the `[Arapuca]` section of the cfg to enable; mesh parameters live in the `_arapuca` group of `utils/globals.py`.

v7 : Consistent with [PERL v7](https://github.com/DUNE/dunecore/blob/develop/dunecore/Geometry/gdml/generate_dunevd10kt_3view_30deg_v7_refactored.pl), but adds Detailed Cryostat Structure (I-beams, Belts, Shield Walls) and Placement in Cavern Hall

v8 : Homogenizes Inner Cryostat Structure (Membrane, Field Cage, CRPs) to latest drawings
- 8a : Cathode thickness, drift distance, and gaseous and liquid argon buffers follow the drawings in all workspaces.
- 8b : CRP borders match the drawings and the TPC is shifted towards the TCO (west) wall.
- 8c : Field-shaper pitch keeps 108 shapers per drift and the field cage sits 5.1 cm outside the CRP edges.
