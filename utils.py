import numpy as np

def distance(x,y,x2,y2):
    return np.linalg.norm(np.array([x,y]) - np.array([x2,y2]))
