NAME=$1

WIRES="${NAME}.gdml"
NOWIRES="${NAME}_nowires.gdml"

gegede-cli larfd.cfg         -o ${WIRES}   -w World ;
gegede-cli larfd_nowires.cfg -o ${NOWIRES} -w World ;
