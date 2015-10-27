cd ../../..
python setup.py develop >& install.out
cd python/duneggd/examples
echo ""
echo ""
gegede-cli lar.cfg -o example.gdml -w "world" -f gdml
