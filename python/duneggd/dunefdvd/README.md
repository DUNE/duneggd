[GeGeDe](https://github.com/brettviren/gegede)-based geometry builder for the DUNE Far Detector-Vertical Drift

- First install GeGeDe by following the instructions in the link above

- Then, one can generate output gdml by running :
```
gegede-cli dunevd_v8.cfg -o dunevd10kt_3view_30deg_v8_full10kt_ggd.gdml
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

World origin : x at the cathode centre (mid-drift for the single drift volume 1x8x14), y at the centre of the active volume, z at the upstream (cryogenics-side) face of the CRP array.

v7 : Consistent with [PERL v7](https://github.com/DUNE/dunecore/blob/develop/dunecore/Geometry/gdml/generate_dunevd10kt_3view_30deg_v7_refactored.pl), but adds Detailed Cryostat Structure (I-beams, Belts, Shield Walls) and Placement in Cavern Hall

v8 : Homogenizes Inner Cryostat Structure (Membrane, Field Cage, CRPs) to latest drawings
- 8a : Cathode thickness (6.1 cm), drift distance (641.2 cm, cold), gaseous argon (49 cm) and liquid argon buffers (33.3 cm above the top CRPs, 29.2 cm below the bottom CRPs, 79.9 cm at the long walls) follow the drawings in all workspaces.
- 8b : CRP borders (0.645 cm) match the drawings and the TPC is shifted 20.45 cm towards the TCO (west) wall, leaving 79.9 cm (TCO) and 120.8 cm (cryogenics) end-wall buffers.
- 8c : Field-shaper pitch (5.92 cm) keeps 108 shapers per drift and the field cage sits 5.1 cm outside the CRP edges.

The shield walls and floor shielding outside the I-beams are off by default; set `Shielding_switch = True` in the cfg to build `full10kt_shielded`.
