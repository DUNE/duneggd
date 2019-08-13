from math import cos, sin, tan, sqrt, pow
import matplotlib.pyplot as plt
import numpy as np
import pint

ureg= pint.UnitRegistry()
Q = ureg.Quantity
Quantity = ureg.Quantity
wirePitch = 0.4669*ureg.cm
wireAngle = 35.7*ureg.deg
view = 'V'
nChannels = 800
planeDim = [Quantity(1520, 'micrometer'), Quantity(5986.27, 'millimeter'), Quantity(2306.36, 'millimeter')]
FirstWireStartPos = [Q('0m'), Q('-2993.135mm'), Q('-1139.71mm')]

# FirstWireStartPos = [0*ureg.m,
#                      -planeDim[1] / 2,
#                      -planeDim[2] / 2 + FirstWireOffset]
SideWrappingBoardOffset = 12.98*ureg.mm - 11.08*ureg.mm
# detDim = [0, 606.635, 229.685]

plt.figure()
# plt.plot([-0.5*detDim[2], -0.5*detDim[2]], [-0.5*detDim[1], 0.5*detDim[1]], "k-")
# plt.plot([ 0.5*detDim[2],  0.5*detDim[2]], [-0.5*detDim[1], 0.5*detDim[1]], "k-")
# plt.plot([-0.5*detDim[2],  0.5*detDim[2]], [-0.5*detDim[1],-0.5*detDim[1]], "k-")
# plt.plot([-0.5*detDim[2],  0.5*detDim[2]], [ 0.5*detDim[1], 0.5*detDim[1]], "k-")

def PlotWire(Start,
             End,
             Color):

    Dim = [2,1]
    plt.plot([Start[Dim[0]].to(ureg.cm).magnitude, End[Dim[0]].to(ureg.cm).magnitude],
             [Start[Dim[1]].to(ureg.cm).magnitude, End[Dim[1]].to(ureg.cm).magnitude],
             "k-", color=Color)
    
def MakeAndPlotWires(wirePitch, wireAngle, view, nChannels, FirstWireStartPos):

    pitch = [0*ureg.cm,
             wirePitch / sin(wireAngle.to('radians')),
             wirePitch / cos(wireAngle.to('radians'))]

    print("*"*3 + " Placing the bottom wires " + "*"*3)
    increment=0
    if view == 'V':
        increment=1
    else:
        increment=-1

    degAboutX = 90*ureg.deg - increment*wireAngle
    nWires = int(0.5*nChannels)

    wire_num = 0
    nwirebottom = 0
    print("FirstWireStartPos :" + str(FirstWireStartPos))
    FirstWireEndPos = [FirstWireStartPos[0],
                       FirstWireStartPos[1] + (planeDim[2]*0.5 - increment*FirstWireStartPos[2]) / tan(wireAngle.to('radians')),
                       increment*planeDim[2]/2]
    
    for i in range(nWires):       
        wireStartPos = [FirstWireStartPos[0],
                        FirstWireStartPos[1],
                        FirstWireStartPos[2] + increment*i*pitch[2]]

        wireEndPos = [wireStartPos[0],
                      FirstWireStartPos[1] + (planeDim[2]*0.5 - increment*wireStartPos[2]) / tan(wireAngle.to('radians')),
                      increment*planeDim[2]/2]
        
        PlotWire(wireStartPos, wireEndPos, 'b')
        wire_num    += 1
        nwirebottom += 1

    print("... placed "+ str(nwirebottom) + " wires.")
    endofplane = False
    # take "advantage" of the wraping here.
    # the end of the last wire will be the next one + a tiny offset visible
    # in 8760024 (the first wire pins are not *exactly* horizontal)
    # of course you have to be very careful of the orientation of the board!
    wireStartPos = [FirstWireEndPos[0],
                    FirstWireEndPos[1],
                    FirstWireEndPos[2]]
    print (wireStartPos)
    
    print("*"*3 + " Placing the middle wires " + "*"*3)
    
    nwiremiddle=0

    while (not endofplane):
        wireStartPos = [wireStartPos[0],
                        wireStartPos[1] + pitch[1],
                        wireStartPos[2]]
        if (wireStartPos[1] >= 0.5*planeDim[1]):
            endofplane = True
            break

        wireEndPos = [wireStartPos[0],
                      wireStartPos[1] - planeDim[2] / tan(wireAngle.to('rad')),
                      - planeDim[2]/2]
        
        wire_num    += 1
        nwiremiddle += 1
        PlotWire(wireStartPos, wireEndPos, 'r')

    print("... placed "+ str(nwiremiddle) + " wires.")


    print("*"*3 + " Placing the top wires    " + "*"*3)

    nwiretop = 0
        
    # here continue to add the wires from the left end by increasing y
    # not the pitch as already be added from the while loop
    wireStartPos = [wireEndPos[0],
                    wireEndPos[1],
                    wireEndPos[2]]
    print(wireStartPos)

    print(nWires)
    for i in range(nWires):
        wireStartPos = [wireStartPos[0],
                        wireStartPos[1] + pitch[1],
                        wireStartPos[2]]
        wireEndPos = [wireStartPos[0],
                      planeDim[1] / 2,
                      - planeDim[2] / 2 + (planeDim[1] / 2 - wireStartPos[1]) * tan(wireAngle.to('radians'))]

        if (wireStartPos[2] >= wireEndPos[2]):
            endofplane = True
            break
            
        wire_length = ((wireEndPos[0] - wireStartPos[0])**2 +
                       (wireEndPos[1] - wireStartPos[1])**2 +
                       (wireEndPos[2] - wireStartPos[2])**2)**0.5
        PlotWire(wireStartPos, wireEndPos, 'b')


        wire_num += 1
        nwiretop += 1
        
    print("... placed "+ str(nwiretop) + " wires.")


MakeAndPlotWires(wirePitch, wireAngle, view, nChannels, FirstWireStartPos)
plt.show()
