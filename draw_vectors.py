import numpy as np
import matplotlib.pyplot as plt


origin = np.array([[0, 0], [0, 0]])
dir = np.array([[1, -1], [1, 1]])

plt.quiver([0, 0], [0, 0], [1, -1], [1, 1], angles='xy', scale_units='xy', scale=1)
plt.xlim(-10, 10)
plt.ylim(-10, 10)
plt.show()
