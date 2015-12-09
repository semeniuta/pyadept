'''
Computational model of the Adept cell geometry
'''
import numpy as np

# Assumptions on coordinate frames
a = 1
b = 1
h = 1
R = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, -1]])
t = np.array([a, b, h])
T_ct = np.hstack((R, t.reshape((3,1))))
