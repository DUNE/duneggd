import numpy as np

from gegede import Quantity as Q

# --- Constant values for wire planes ---
WireDiam     = Q("15um")

UWirePitch   = Q("0.46681300000000003cm")
VWirePitch   = Q("0.46681300000000003cm")
XWirePitch   = Q("0.479cm")

WireAngle    = Q("35.710deg")

planeDimZ    = [Q("152um"), Q("598.39cm")  , Q("229.593cm")]
planeDimV    = [Q("152um"), Q("598.7075cm"), Q("230.0025cm")]
planeDimU    = [Q("152um"), Q("599.025cm") , Q("230.6375cm")]

# UWire_yint   = Q("0.7995779382797346253987cm")
# UWire_zint   = Q("0.5747666711641606322877cm")
# VWire_yint   = Q("0.7995779382797346253987cm")
# VWire_zint   = Q("0.5747666711641606322877cm")

UWire_yint   = UWirePitch / np.sin(WireAngle.to("rad").magnitude)
UWire_zint   = UWirePitch / np.cos(WireAngle.to("rad").magnitude)
VWire_yint   = VWirePitch / np.sin(WireAngle.to("rad").magnitude)
VWire_zint   = VWirePitch / np.cos(WireAngle.to("rad").magnitude)

UWireOffset  = Q("0.764195192922017cm")
VWireOffset  = Q("0.5cm")

#  __   __  _____  _                  
#  \ \ / / |  __ \| |                 
#   \ V /  | |__) | | __ _ _ __   ___ 
#    > <   |  ___/| |/ _` | '_ \ / _ \
#   / . \  | |    | | (_| | | | |  __/
#  /_/ \_\ |_|    |_|\__,_|_| |_|\___|
#

def MakeCollectionPlane(planeDim):

    WirePlaneZ = open("WirePlaneZ.txt", "w")

    wirePos = (-0.5*XWirePitch) - (239*XWirePitch)

    index = 0
    while (wirePos < 0.5*planeDim[2]):

        WirePlaneZ.write(str(wirePos.to("mm").magnitude)            + "\t" +
                         str((-0.5*planeDim[1]).to("mm").magnitude) + "\t" +
                         str(wirePos.to("mm").magnitude)            + "\t" +
                         str((0.5*planeDim[1]).to("mm").magnitude)  + "\n")

        index += 1
        wirePos += XWirePitch
    print("DONE CREATING - " + str(index) + " - Collection wires")

#  _    _   _____  _                  
# | |  | | |  __ \| |                 
# | |  | | | |__) | | __ _ _ __   ___ 
# | |  | | |  ___/| |/ _` | '_ \ / _ \
# | |__| | | |    | | (_| | | | |  __/
#  \____/  |_|    |_|\__,_|_| |_|\___|
#
        
def MakeInductionPlaneU(planeDim):

    WirePlaneU = open("WirePlaneU.txt", "w")

    index      = 0
    zpos       = (-0.5*planeDim[2]) + UWireOffset
    ypos       = UWireOffset / np.tan(WireAngle.to("rad").magnitude)

    # Placing the bottom corner wires
    while (zpos < 0.5*planeDim[2]):
        
        WirePlaneU.write(str((-0.5*planeDim[2]).to("mm").magnitude) + "\t" +
                         str(ypos.to("mm").magnitude)               + "\t" +
                         str((zpos).to("mm").magnitude)               + "\t" +
                         str(Q("0m").to("mm").magnitude)            + "\n")
        index += 1
        zpos  += UWire_zint
        ypos  += UWire_yint

    print(index)        
    # Placing the center wires
    while (ypos < planeDim[1]):
        ylow = ypos - (planeDim[2] / np.tan(WireAngle.to("rad").magnitude))
    
        WirePlaneU.write(str((-0.5*planeDim[2]).to("mm").magnitude)            + "\t" +
                         str(ypos.to("mm").magnitude) + "\t" +
                         str((0.5*planeDim[2]).to("mm").magnitude)            + "\t" +
                         str(ylow.to("mm").magnitude)  + "\n")
        ypos  += UWire_yint
        index += 1

    print(index)
    ypos -= (planeDim[2] / np.tan(WireAngle.to("rad").magnitude))
    zpos  = (0.5*planeDim[2]) - ((1*planeDim[1] - ypos) * np.tan(WireAngle.to("rad").magnitude))
    # while (ypos < planeDim[1]):
    for i in range(400):
        WirePlaneU.write(str((zpos).to("mm").magnitude)              + "\t" +
                         str(planeDim[1].to("mm").magnitude)       + "\t" +
                         str((0.5*planeDim[2]).to("mm").magnitude) + "\t" +
                         str(ypos.to("mm").magnitude)              + "\n")
        index += 1
        ypos  += UWire_yint
        zpos  += UWire_zint
        
    WirePlaneU.close()
    print("DONE CREATING - " + str(index) + " - U Plane wires")
        
#  __      __  _____  _                  
#  \ \    / / |  __ \| |                 
#   \ \  / /  | |__) | | __ _ _ __   ___ 
#    \ \/ /   |  ___/| |/ _` | '_ \ / _ \
#     \  /    | |    | | (_| | | | |  __/
#      \/     |_|    |_|\__,_|_| |_|\___|
#   

def MakeInductionPlaneV(planeDim):

    WirePlaneV = open("WirePlaneV.txt", "w")

    index = 0
    zpos  = (0.5*planeDim[2]) - VWireOffset
    ypos  = VWireOffset / np.tan(WireAngle.to('rad').magnitude)

    # Placing the bottom corner wires
    while (zpos > -0.5*planeDim[2]):
        WirePlaneV.write(str(zpos.to("mm").magnitude)             + "\t" +
                         str(0)                                   + "\t" +
                         # str(-0.5*planeDim[1].to("mm").magnitude) + "\t" +
                         str(0.5*planeDim[2].to("mm").magnitude)  + "\t" +
                         str(ypos.to("mm").magnitude)             + "\n")
        print(zpos, ypos)

        index += 1
        zpos  -= VWire_zint
        ypos  += VWire_yint

    # print(index)
    # # Placing the center wires
    # while (ypos < 0.5*planeDim[1]):

    #     ylow = ypos - (planeDim[2] / np.tan(WireAngle.to("rad").magnitude))
    #     WirePlaneV.write(str((-0.5*planeDim[2]).to("mm").magnitude) + "\t" +
    #                      str((ylow+(0.5*planeDim[1])).to("mm").magnitude)               + "\t" +
    #                      str((0.5*planeDim[2]).to("mm").magnitude)  + "\t" +
    #                      str((ypos+(0.5*planeDim[1])).to("mm").magnitude)               + "\n")
    #     index      += 1
    #     ypos       += VWire_yint

    # print(index)       
    # # Placign the top corner wires
    # ypos -= (planeDim[2] / np.tan(WireAngle.to("rad").magnitude))
    # zpos  = (-0.5*planeDim[2]) + ((0.5*planeDim[1] - ypos) * np.tan(WireAngle.to("rad").magnitude))
    # # while (ypos < 0.5*planeDim[1]):
    # for i in range(400):
    #     WirePlaneV.write(str((-0.5*planeDim[2]).to("mm").magnitude) + "\t" +
    #                      str((ypos+(0.5*planeDim[1])).to("mm").magnitude)               + "\t" +
    #                      str(zpos.to("mm").magnitude)               + "\t" +
    #                      str((planeDim[1]).to("mm").magnitude)  + "\n")

    #     index += 1
    #     ypos  += VWire_yint
    #     zpos  -= VWire_zint

    WirePlaneV.close()
    print("DONE CREATING - " + str(index) + " - V Plane wires")
        
def main(x, u, v):

    if (x) : MakeCollectionPlane(planeDimZ)
    if (u) : MakeInductionPlaneU(planeDimU)
    if (v) : MakeInductionPlaneV(planeDimV)
    

main(0, 0, 1)    
