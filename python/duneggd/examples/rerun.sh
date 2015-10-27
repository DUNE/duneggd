cd ../../..
python setup.py develop >& install.out
cd python/gegede/examples
echo ""
echo ""
gegede-cli lar.cfg -o example.gdml -w "world" -f gdml
