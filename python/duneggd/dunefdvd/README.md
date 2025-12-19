[GeGeDe](https://github.com/brettviren/gegede)-based geometry builder for the DUNE Far Detector-Vertical Drift

- First install GeGeDe by following the instructions in the link above

- Then, one can generate output gdml by running :
```
gegede-cli dunevd_v6.cfg -o dunevd_v6_full10kt_support_cavern.gdml
```

May have to add current directory to `PYTHONPATH` before doing so with :

```
export PYTHONPATH=`pwd`:$PYTHONPATH
```

The file : `dunevd_v6.cfg` stores the configuration parameters and builder hierarchy. It uses defaults from `utils/globals.py`.
Currently it constructs the full 10kt VD geometry along with the cavern hall, current support structure design and other details.
Apply `simple=True` within it to default back to the simplified "workspace"-type geometries that many simulations use.
For visualization, one can refer to `gl.C` or `geoDisplay.C` (former having more flexibility in turning on-off certain volumes)
For checking overlaps, one can run `check_overlap.C`
