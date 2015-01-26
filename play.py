#!/usr/bin/python

import os
import sys
import math


###
def array_check(arr):
    N = len(arr)
    combis = [(i, ) for i in xrange(N)]
    for i in xrange(2, N+1):
        cur_combis = []
        for c in combis:
            if len(c) < i-1: continue
            for j in xrange(c[-1] + 1, N):
                # print c, j,  '->', c + (j,)
                cur_combis.append(c + (j,))
        combis += cur_combis    
    
    return combis


###
def main(argv):
    return None

if __name__ == '__main__': main(sys.argv[1:])
