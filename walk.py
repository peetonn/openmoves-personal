import numpy as np
import numpy.random as rnd

dt = 1

def walk(x, v):
    a = rnd.randn()
    x = x + v * dt + 0.5 * a * dt * dt
    v = v + a * dt
    return x, v

def dowalk(x0, v0, n):
    x = x0
    v = v0
    xes = np.zeros(n+1)
    i = 0
    vs = []
    while i <= n:
        xes[i] = x
        vs.append(v)
        x, v = walk(x, v)
        i = i + 1
    return xes, vs