import matplotlib.pyplot as plt
import numpy as np

data = np.loadtxt("U-low-wires.txt")

detDim = [0, 606.635, 229.685]

plt.figure()
plt.plot([-0.5*detDim[2], -0.5*detDim[2]], [-0.5*detDim[1], 0.5*detDim[1]], "k-")
plt.plot([ 0.5*detDim[2],  0.5*detDim[2]], [-0.5*detDim[1], 0.5*detDim[1]], "k-")
plt.plot([-0.5*detDim[2],  0.5*detDim[2]], [-0.5*detDim[1],-0.5*detDim[1]], "k-")
plt.plot([-0.5*detDim[2],  0.5*detDim[2]], [ 0.5*detDim[1], 0.5*detDim[1]], "k-")


wires = len(data[:, 0])
x = data[:, 0]
y = data[:, 1]
z = data[:, 2]

for i in range(wires):
    plt.plot([-0.5*detDim[2], -0.5*detDim[2] + abs(z[i])], [-0.5*detDim[1] + abs(y[i]), -0.5*detDim[1]], "k-")

plt.show()
