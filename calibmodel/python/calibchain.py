import numpy as np

def homog_one(x):
    div = np.array([1.0/x[-1] for i in range(x.shape[0])])
    return x * div
    
def get_divbyz(x_cam):
    z = x_cam[2]
    A = 1.0/z * np.eye(3)
    b = np.zeros((3, 1))
    return np.hstack((A, b))
    
def distort(x_projected, dc):
    pass 
    
a = np.array([1, 2, 3, 4])
