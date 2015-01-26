#!/usr/bin/env python

import sys
import math
import numpy as np

def sandY(x):
    return -263.733 * x**2 + 448.736 * x + 46.2071 * x**-1 + 5.62961 * x**-2   
def peatY(x):
    return -129.503 + x**2 + 400 * x - 162.82 + 147.748 * x**-1 + 20.7454 * x**-2 


def peatLogY(x):
    return -12123.1 + (285.795-(-12123.1))/(1+2.33526e06*math.exp(-23.553*x))**(1/-339.175)
def sandLogY(x):
    return 1.10307e06 + (275.011-1.10307e06)/(1+1.24324e06*math.exp(-41.3028*x))**(1/36119.7)


def searchX(y_query, Pn, lb=0.0, ub=1.0, eps=0.001, it=20):
    x = abs(ub - lb) / 2 
    y = Pn(x)
    if abs(y_query - y) <= eps or it == 0:
        return x
    if y < y_query:
        ub = x
    else:
        lb = x
    return searchX(y_query, Pn, lb=lb, ub=ub, it=it-1)
    
    
def compute_LUT(func):
    lut = dict()
    for x in np.arange(0.0, 1.0, 0.001):
        y = func(x)
        rd_y= int(round(y))
        lut[rd_y] = lut.get(rd_y, []) + [x]
    for k in lut:
        lut[k] = sum(lut[k])/len(lut[k])
    return lut



def main(argv):
     
    lut = compute_LUT(peatLogY)
    for i in np.arange(100,600,10):
        try:
            print i, lut[i]
        except:
            print i, 'no entry'

    
    pass


if __name__ == '__main__': main(sys.argv[1:])



