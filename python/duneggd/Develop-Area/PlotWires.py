import numpy as np
import matplotlib.pyplot as plt

wires = np.loadtxt("WirePlaneU.txt")

plt.figure()
for i in range(len(wires[:, 1])):

    xPoints = [wires[:, 0][i]/10, wires[:, 2][i]/10]
    yPoints = [wires[:, 1][i]/10, wires[:, 3][i]/10]

    plt.plot(xPoints, yPoints, "k-")

plt.show()    
    
