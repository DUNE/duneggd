[GeGeDe](https://github.com/brettviren/gegede)-based geometry builder for the DUNE Far Detector-Vertical Drift

- First install GeGeDe by following the instructions in the link above

- Then, one can generate output gdml by running :
```
gegede-cli dunevd_v6.cfg -o dunevd10kt_v6_full10kt_support_cavern.gdml
```

May have to add current directory to `PYTHONPATH` before doing so with :

```
export PYTHONPATH=`pwd`:$PYTHONPATH
```

The file : `dunevd_v6.cfg` stores the configuration parameters and builder hierarchy. It uses defaults from `utils/globals.py`.
Currently default configuration is to construct the full 10kt VD geometry along with the cavern hall, current support structure design and other details (see below image).

<img width="1916" height="1077" alt="Screen Shot 2025-12-18 at 19 10 08" src="https://github.com/user-attachments/assets/25448fae-a2fc-442b-8fac-b704d3905e5d" />

Apply `simple=True` and the appropriate `workspace` option within it to default back to the simplified "workspace"-type geometries that many simulations use. For example :
```
workspace = 3 and simple = True : 1x8x6
workspace = 4 and simple = True : 1x8x14
```

For visualization, one can refer to `gl.C` or `geoDisplay.C` (former having more flexibility in turning on-off certain volumes)
For checking overlaps, one can run `check_overlap.C`
