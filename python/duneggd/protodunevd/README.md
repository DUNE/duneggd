## Set up on dunegpvm

We need the GeGeDe source code since some shapes are added recently, not propagated to python virtual env.
Install:
```
cd /exp/dune/app/users/weishi/PDVDGeo
git clone https://github.com/brettviren/gegede.git

mkdir gegede_install
cd gegede/
python setup.py install --prefix /exp/dune/app/users/weishi/PDVDGeo/gegede_install
export PYTHONPATH=/exp/dune/app/users/weishi/PDVDGeo/gegede_install/lib/python3.9/site-packages/gegede-0.8-py3.9.egg:$PYTHONPATH
export PATH=/exp/dune/app/users/weishi/PDVDGeo/gegede_install/bin:${PATH}  # where gegede-cli executable is

# install lxml for export gdml
pip install --target=/exp/dune/app/users/weishi/gdmlexportlibs pint lxml
export PYTHONPATH=/exp/dune/app/users/weishi/gdmlexportlibs:$PYTHONPATH

```

```
cd /exp/dune/app/users/weishi/PDVDGeo
[rsync local changes] git clone https://github.com/weishi10141993/duneggd.git
cd duneggd
export PYTHONPATH=`pwd`/python/duneggd/protodunevd:$PYTHONPATH # so that python knows where to look for import modules

gegede-cli python/duneggd/protodunevd/protodune_vd.cfg -o protodune.gdml

# to generate nowires version, set "wires_on" in the cfg to False
# to include Dual Phase CRT, set "DP_CRT_switch" in the cfg to True
```

Relogin setup:
```
cd /exp/dune/app/users/weishi/PDVDGeo/
cd duneggd
export PYTHONPATH=/exp/dune/app/users/weishi/PDVDGeo/gegede_install/lib/python3.9/site-packages/gegede-0.8-py3.9.egg:$PYTHONPATH
export PATH=/exp/dune/app/users/weishi/PDVDGeo/gegede_install/bin:${PATH}  # where gegede-cli executable is

export PYTHONPATH=/exp/dune/app/users/weishi/gdmlexportlibs:$PYTHONPATH
export PYTHONPATH=`pwd`/python/duneggd/protodunevd:$PYTHONPATH

gegede-cli python/duneggd/protodunevd/protodune_vd.cfg -o protodune.gdml
```

## Note on gdml header
Replace the above generated gdml headers with the following Schema otherwise LArSoft complains:
```
<?xml version="1.0" encoding="UTF-8" ?>
<gdml_simple_extension xmlns:gdml_simple_extension="http://www.example.org"
                       xmlns:xs="http://www.w3.org/2001/XMLSchema-instance"
                       xs:noNamespaceSchemaLocation="RefactoredGDMLSchema/SimpleExtension.xsd">



</gdml_simple_extension>
```

## Check overlaps

```
source /cvmfs/larsoft.opensciencegrid.org/spack-packages/setup-env.sh
spack load root@6.28.12
root -l -b -q  check_overlap.C
```
