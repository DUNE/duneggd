import numpy as np
import scipy as sp

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import mpl_toolkits.mplot3d as a3


from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.collections import PolyCollection


# --- The input parameters from the fhicl file
X0 = [  -990.0,  -990.0,  -991.0,   990.0,  -990.0, -990.0  ]  
Y0 = [  -889.0,  1428.0,  -888.0,  -888.0,  -888.0, -888.0  ]
Z0 = [  -536.0,  -536.0,  -536.0,  -536.0, 14534.0, -537.0  ]

X1 = [   990.0,   990.0,  -990.0,   991.0,   990.0,  990.0  ]
Y1 = [  -888.0,  1429.0,  1428.0,  1428.0,  1428.0, 1428.0  ]
Z1 = [ 14534.0, 14534.0, 14534.0, 14534.0, 14535.0, -536.0  ]

# --- Work out the vertices
def GetVertices(j):
    x = []
    y = []
    z = []
    
    maxValue = 0
    for i in range(len(X0)):
        if (X0[i] > maxValue): maxValue = X0[i]
        if (Y0[i] > maxValue): maxValue = Y0[i]
        if (Z0[i] > maxValue): maxValue = Z0[i]
        if (X1[i] > maxValue): maxValue = X1[i]
        if (Y1[i] > maxValue): maxValue = Y1[i]
        if (Z1[i] > maxValue): maxValue = Z1[i]


    x.append(X0[j]) ; x.append(X0[j]) ; x.append(X0[j]) ; x.append(X0[j])
    z.append(Z0[j]) ; z.append(Z0[j]) ; z.append(Z1[j]) ; z.append(Z1[j])    
    y.append(Y0[j]) ; y.append(Y1[j]) ; y.append(Y1[j]) ; y.append(Y0[j])
    x.append(X1[j]) ; x.append(X1[j]) ; x.append(X1[j]) ; x.append(X1[j])
    z.append(Z0[j]) ; z.append(Z0[j]) ; z.append(Z1[j]) ; z.append(Z1[j])    
    y.append(Y0[j]) ; y.append(Y1[j]) ; y.append(Y0[j]) ; y.append(Y1[j])

    x = [j/maxValue for j in x]
    y = [j/maxValue for j in y]
    z = [j/maxValue for j in z]

    return(list(zip(x, y, z)))

killMe = [GetVertices(i) for i in range(6)]

ax = a3.Axes3D(plt.figure())
for i in range(len(killMe)):
    vtx = killMe[i]
    tri = a3.art3d.Poly3DCollection([vtx])
    tri.set_color(colors.rgb2hex(sp.rand(3)))
    tri.set_edgecolor('k')
    ax.add_collection3d(tri)

plt.xlabel("x")
plt.ylabel("y")

plt.show()
