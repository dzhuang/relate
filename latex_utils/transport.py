# -*- coding: utf-8 -*-

import numpy as np
from collections import Counter


def transport(supply, demand, costs):

    # Only solves balanced problem
    assert sum(supply) == sum(demand)

    s = np.copy(supply)
    d = np.copy(demand)
    C = np.copy(costs)

    n, m = C.shape

    # Finding initial solution
    #X = np.zeros((n, m))
    X = np.full((n, m), np.nan)
    allow_fill_X = np.ones((n, m), dtype=bool)
    indices = [(i, j) for i in range(n) for j in range(m)]

    # 最小元素法
    xs = sorted(zip(indices, C.flatten()), key=lambda (a, b): b)

    # 西北角法
    #xs = sorted(zip(indices, C.flatten()), key=lambda (a, b): (a[0],a[1]))

    #print xs

    # Iterating C elements in increasing order
    for (i, j), _ in xs:
        # if d[j] == 0:
        #     continue
        # else:
        #     # Reserving supplies in a greedy way
        #     #print min([s[i], d[j]])
        #     remains = s[i] - d[j] if s[i] >= d[j] else 0
        #     grabbed = s[i] - remains
        #     X[i, j] = grabbed
        #     s[i] = remains
        #     d[j] -= grabbed
        grabbed = min([s[i],d[j]])
        #print grabbed
        if grabbed == 0:
            continue
        elif not np.isnan(X[i,j]):
            # X[i,j]单元格未填数字
            continue
        else:
            # 行与列同时满足，退化（除非是最后一个单元格）
            X[i, j] = grabbed
            if s[i] == grabbed and d[j] == grabbed:
                allow_fill_X[i, j] = False
                allowed_indices = [(ii, jj) for ii in range(n) for jj in range(m) if allow_fill_X[ii,jj]]
                if allowed_indices:
                    # 在允许填写数字的单元格补0
                    X[allowed_indices[0]] = 0
                    allow_fill_X[allowed_indices[0]] = False
            s[i] -= grabbed
            d[j] -= grabbed
        #print s[i], d[j]

        if d[j] == 0:
            allow_fill_X[:,j] = False
        if s[i] == 0:
            allow_fill_X[i,:] = False

        #print allow_fill_X



    print 'solution is', X
    # Finding optimal solution
    while True:
        u = np.array([np.nan]*n)
        v = np.array([np.nan]*m)
        S = np.zeros((n, m))

        #_x, _y = np.where(X > 0)
        _x, _y = np.where(~np.isnan(X))
        nonzero = zip(_x, _y)
        print nonzero
        f = nonzero[0][0]
        u[f] = 0

        # Finding u, v potentials
        while any(np.isnan(u)) or any(np.isnan(v)):
            for i, j in nonzero:
                if np.isnan(u[i]) and not np.isnan(v[j]):
                    u[i] = C[i, j] - v[j]
                elif not np.isnan(u[i]) and np.isnan(v[j]):
                    v[j] = C[i, j] - u[i]
                else:
                    continue

        # Finding S-matrix
        for i in range(n):
            for j in range(m):
                S[i, j] = C[i, j] - u[i] - v[j]

        print 's-matrix is ', S

        # Stop condition
        s = np.min(S)
        if s >= 0:
            #print 'Final solution is', X
            break

        i, j = np.argwhere(S == s)[0]
        start = (i, j)

        # Finding cycle elements
        T = np.copy(X)
        T[start] = 1
        while True:
            _xs, _ys = np.nonzero(T)
            xcount, ycount = Counter(_xs), Counter(_ys)

            for x, count in xcount.items():
                if count <= 1:
                    T[x,:] = 0
            for y, count in ycount.items():
                if count <= 1: 
                    T[:,y] = 0

            if all(x > 1 for x in xcount.values()) \
                    and all(y > 1 for y in ycount.values()):
                break
        
        # Finding cycle chain order
        dist = lambda (x1, y1), (x2, y2): abs(x1-x2) + abs(y1-y2)
        fringe = set(tuple(p) for p in np.argwhere(T > 0))

        size = len(fringe)

        path = [start]
        while len(path) < size:
            last = path[-1]
            if last in fringe:
                fringe.remove(last)
            next = min(fringe, key=lambda (x, y): dist(last, (x, y)))
            path.append(next)

        # Improving solution on cycle elements
        neg = path[1::2]
        pos = path[::2]
        q = min(X[zip(*neg)])
        X[zip(*neg)] -= q
        X[zip(*pos)] += q
        #print 'solution is', X

    return X, np.sum(X*C)


if __name__ == '__main__':
    supply = np.array([110, 350, 390])
    demand = np.array([270, 130, 190, 150, 110])

    #from sympy import *

    costs = np.array([[24., 50., 55., 27., 16.],
                      [50., 40., 23., 17., 21.],
                      [35., 59., 55., 27., 41.]])

    routes, z = transport(supply, demand, costs)
    #assert z == 23540

    #print routes