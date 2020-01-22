import matplotlib.pyplot as plt
import numpy as np
import math as m

# Dimensions and numbers that are not changed #
APA_dy          = 606        # [cm]
APA_dz          = 231.59     # [cm]
n_wires         = 400
wire_angle      = 35.701     # [deg]
first_wire_U    = 0.55
first_wire_V    = 0.5
pitch           = 0.4667
wirepitch       = [0, pitch/np.sin(m.radians(35.710)), pitch/np.cos(m.radians(35.710))]
center_wire_mid = [] 

plt.figure("APA-Frame")
plt.plot([-10, APA_dz]     , [0, 0]          , "k-")
plt.plot([-10, APA_dz]     , [APA_dy, APA_dy], "k-")
plt.plot([0, 0]          , [0, APA_dy]     , "k-")
plt.plot([APA_dz, APA_dz], [0, APA_dy]     , "k-")

def makeLowWire(length, angle, mid, view, drawInversion=False):

    wire_line = [[], []]
    if (view == "U"):
        wire_line[0].append(0)
        wire_line[0].append(length * np.sin(m.radians(angle)))
        wire_line[1].append(wire_line[0][1] / np.tan(m.radians(angle)))
        wire_line[1].append(0)

        if (drawInversion == True):
            plt.plot([APA_dz-wire_line[0][0], APA_dz-wire_line[0][1]], wire_line[1], "-", color="gray")
            
    if (view == "V"):
        wire_line[0].append(APA_dz - (2 * mid))
        wire_line[0].append(APA_dz)
        wire_line[1].append(0)
        wire_line[1].append(length * np.cos(m.radians(angle)))

    return wire_line

def makeMiddleWires(length, angle, mid, half, view, drawInversion=False):

    wire_line = [[], []]
    if (view == "U"):
        wire_line[0].append(0)
        wire_line[0].append(APA_dz)
        wire_line[1].append(mid + half)
        wire_line[1].append(mid - half)

    if (view == "V"):
        wire_line[0].append(0)
        wire_line[0].append(APA_dz)
        wire_line[1].append(mid + half)
        wire_line[1].append(mid - half)
        
    return wire_line
            
def makeTopWires(length, angle, mid, half, view, drawInversion=False):            

    wire_line = [[], []]
    if (view == "U"):
        wire_line[0].append(APA_dz - length * np.sin(m.radians(angle)))
        wire_line[0].append(APA_dz)
        wire_line[1].append(APA_dy)
        wire_line[1].append(mid[1] - half)

    if (view == "V"):
        wire_line[0].append(0)
        wire_line[0].append(length * np.cos(m.radians(angle)))
        wire_line[1].append(mid[1] - half)
        wire_line[1].append(APA_dy)

    return wire_line

            
#  __  __       _    _               _    _            _               
# |  \/  |     | |  (_)             | |  | |          (_)              
# | \  / | __ _| | ___ _ __   __ _  | |  | | __      ___ _ __ ___  ___ 
# | |\/| |/ _` | |/ / | '_ \ / _` | | |  | | \ \ /\ / / | '__/ _ \/ __|
# | |  | | (_| |   <| | | | | (_| | | |__| |  \ V  V /| | | |  __/\__ \
# |_|  |_|\__,_|_|\_\_|_| |_|\__, |  \____/    \_/\_/ |_|_|  \___||___/
#                             __/ |                                    
#                            |___/                                     

mid_point_U = first_wire_U/2
wire_ends = [0, 0]
nWires = 0
while (mid_point_U <= APA_dz/2):
    lenWire      = 2 * mid_point_U / np.sin(m.radians(wire_angle))    
    wire_done    = makeLowWire(lenWire, wire_angle, mid_point_U, "U", False)
    wire_ends[0] = wire_ends[1]
    wire_ends[1] = wire_done[1][0]
    mid_point_U += wirepitch[2]
    nWires += 1
    plt.plot(wire_done[0], wire_done[1], "k-")
    
lenWire          = 2 * mid_point_U / np.sin(m.radians(wire_angle))
wire_done        = makeLowWire(lenWire, wire_angle, mid_point_U, "U", False)
line_gradient    = (wire_done[1][1] - wire_done[1][0]) / (wire_done[0][1] - wire_done[0][0])
line_coords      = [[0, APA_dz], [wire_done[1][0], line_gradient*APA_dz + wire_done[1][0]]]
line_half        = (line_coords[1][0] - line_coords[1][1]) / 2
line_middle      = (line_coords[1][0] + line_coords[1][1]) / 2

middle = line_middle
while (middle + line_half < APA_dy):
    wire_done = makeMiddleWires(lenWire, wire_angle, middle, line_half, "U")
    middle += wire_ends[1] - wire_ends[0]
    nWires += 1
    plt.plot(wire_done[0], wire_done[1], "k-")

wire_done        = makeMiddleWires(lenWire, wire_angle, middle, line_half, "U")
line_coords      = [[(APA_dy - wire_done[1][0])/line_gradient, APA_dz], [APA_dy, wire_done[1][1]]]
line_middle_z    = (line_coords[0][1] + line_coords[0][0]) / 2
line_middle_y    = (line_coords[1][1] + line_coords[1][0]) / 2
line_half_y      = (line_coords[1][0] - line_coords[1][1]) / 2

middle = [line_middle_z, line_middle_y]
while (middle[0] < APA_dz):

    lenWire   = 2 * (APA_dz - middle[0]) / np.sin(m.radians(wire_angle))
    wire_done = makeTopWires(lenWire, wire_angle, middle, line_half_y, "U")
    nWires += 1

    plt.plot(wire_done[0], wire_done[1], "k-")
    middle[0] += wirepitch[2]
    middle[1] += wire_ends[1] - wire_ends[0]

print("Number of wires: " + str(nWires))

    

#  __  __       _    _              __      __           _               
# |  \/  |     | |  (_)             \ \    / /          (_)              
# | \  / | __ _| | ___ _ __   __ _   \ \  / /  __      ___ _ __ ___  ___ 
# | |\/| |/ _` | |/ / | '_ \ / _` |   \ \/ /   \ \ /\ / / | '__/ _ \/ __|
# | |  | | (_| |   <| | | | | (_| |    \  /     \ V  V /| | | |  __/\__ \
# |_|  |_|\__,_|_|\_\_|_| |_|\__, |     \/       \_/\_/ |_|_|  \___||___/
#                             __/ |                                      
#                            |___/                                       

mid_point_V = first_wire_V/2
wire_ends = [0, 0]

while (mid_point_V <= APA_dz/2):
    lenWire      = 2 * mid_point_V / np.sin(m.radians(wire_angle))
    wire_done    = makeLowWire(lenWire, -wire_angle, mid_point_V, "V")
    wire_ends[0] = wire_ends[1]
    wire_ends[1] = wire_done[1][1]
    mid_point_V += wirepitch[2]    

    plt.plot(wire_done[0], wire_done[1], "r-")

lenWire          = 2 * mid_point_V / np.sin(m.radians(wire_angle))
wire_done        = makeLowWire(lenWire, wire_angle, mid_point_V, "V", False)
line_gradient    = (wire_done[1][1] - wire_done[1][0]) / (wire_done[0][1] - wire_done[0][0])
line_intercept   = wire_done[1][1] - APA_dz*line_gradient
line_coords      = [[0, APA_dz], [line_intercept, wire_done[1][1]]]
line_half        = (line_coords[1][0] - line_coords[1][1]) / 2
line_middle      = (line_coords[1][0] + line_coords[1][1]) / 2

middle = line_middle
while (middle - line_half < APA_dy):
    wire_done = makeMiddleWires(lenWire, wire_angle, middle, line_half, "V")
    middle += wire_ends[1] - wire_ends[0]
    plt.plot(wire_done[0], wire_done[1], "r-")



wire_done        = makeMiddleWires(lenWire, wire_angle, middle, line_half, "V")
line_coords      = [[0, (APA_dy - wire_done[1][0])/line_gradient], [wire_done[1][0], APA_dy]]
line_middle_z    = (line_coords[0][1]) / 2
line_middle_y    = (line_coords[1][1] + line_coords[1][0]) / 2
line_half_y      = (line_coords[1][1] - line_coords[1][0]) / 2

middle = [line_middle_z, line_middle_y]
while (middle[0] > 0):

    lenWire = 2 * middle[0] / np.cos(m.radians(wire_angle))
    wire_done = makeTopWires(lenWire, wire_angle, middle, line_half_y, "V")
    
    plt.plot(wire_done[0], wire_done[1], "r-")
    middle[0] -= wirepitch[2]
    middle[1] += wire_ends[1] - wire_ends[0]



    
plt.show()    















