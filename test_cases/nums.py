import numpy as np

data = np.random.uniform(-200, 200, size=(4096, 2))

np.savetxt("data4096.txt", data)
