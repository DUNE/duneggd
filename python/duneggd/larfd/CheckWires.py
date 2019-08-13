import matplotlib.pyplot as plt
import numpy as np

def MakeWirePlot(view):
    data = np.loadtxt("WirePos"+view+".txt")

    wires = len(data[:, 0])
    xstart = data[:, 1]
    ystart = data[:, 2]
    zstart = data[:, 3]
    xend   = data[:, 4]
    yend   = data[:, 5]
    zend   = data[:, 6]

    for i in range(wires):
        # print (str(zstart[i]) + " " + str(ystart[i]) + " " + str(zend[i]) + " " + str(yend[i]))
        plt.plot([zstart[i],zend[i]], [ystart[i],yend[i]], "k-")


MakeWirePlot('V')
plt.show()
