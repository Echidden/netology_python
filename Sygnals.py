import numpy as np
import matplotlib.pyplot as plt
axisX = np.arange(0, 1, 0.001)
axisY = []
t=0
for i in range (1000):
    if t>0.4:
        t=t-0.4
    if t<0.3: 
        axisY.append(0.5)
    elif t<0.35:
        axisY.append((t-0.3)*70 + 0.5)
    else: 
        axisY.append((-t+0.4)*70 + 0.5)
    t=t+0.001
plt.plot(axisX, axisY)
plt.show()