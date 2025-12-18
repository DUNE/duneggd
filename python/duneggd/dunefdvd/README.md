[GeGeDe](https://github.com/brettviren/gegede)-based geometry builder for the DUNE Far Detector-Vertical Drift

- First install GeGeDe by following the instructions in the link above

- Then, one can generate output gdml by running : 
```
gegede-cli dunevd_v6.cfg -o dunevd_v6_full10kt.gdml
```

May have to add current directory to `PYTHONPATH` before doing so with : 

```
export PYTHONPATH=`pwd`:$PYTHONPATH
```
