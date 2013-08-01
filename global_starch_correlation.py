#!/usr/bin/env python
'''
Created on Jul 31, 2013

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys

import csv

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats

def linearfit(x, y):
    A = np.vstack([x,np.ones(len(x))]).T
    m,c = np.linalg.lstsq(A,np.array(y))[0]
    return m, c


def plot_yieldCV_yieldCV(x, y, color):
    x = np.array(x)
    y = np.array(y)

    #pearR, pearP = np.corrcoef(x,y)[0:, 0]
    pearR, pearP = scipy.stats.pearsonr(x, y)
    # least squares from:
    # http://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.lstsq.html
    m, c = linearfit(x, y)

    fig = plt.figure()
    # fig.suptitle("argv[1]")
    # plt.scatter(x,y,label='Data '+color,color=color)
    plt.scatter(x,y)#,label='Data '+color,color=color)
    plt.plot(x,x*m+c,color=color,
             label="r = %.5f  P = %6.2e" % (pearR, pearP))
             #label="Fit %6s, r = %6.2e"%(color,pearR))
    #plt.xticks(xMap.values(),xMap.keys())
    
    plt.legend(loc=2)
    plt.xlabel('CV_Staerkeertrag[g/plant] 2011', fontsize=18)
    plt.ylabel('CV_Staerkeertrag[g/plant] 2012', fontsize=18)
    # plt.setp(plt.xticks()[1], rotation=90)    
    plt.subplots_adjust(bottom=0.14)
    # plt.show()
    
    plt.savefig('CV_yield_2011vs2012.svg')
    plt.savefig('CV_yield_2011vs2012.png')
    
    pass

def plot_yieldCV_yieldmedian(x, y, color,year):
    x = np.array(x)
    y = np.array(y)

    #pearR = np.corrcoef(x,y)[1,0]
    #pearR, pearP = np.corrcoef(x,y)[0:, 0]
    pearR, pearP = scipy.stats.pearsonr(x, y)
    # least squares from:
    # http://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.lstsq.html
    m, c = linearfit(x, y)

    fig = plt.figure()
    # fig.suptitle("argv[1]")
    # plt.scatter(x,y,label='Data '+color,color=color)
    plt.scatter(x,y)#,label='Data '+color,color=color)
    plt.plot(x,x*m+c,color=color,
             label="r = %.5f  P = %6.2e" % (pearR, pearP))
             #label="Fit %6s, r = %6.2e"%(color,pearR))
    #plt.xticks(xMap.values(),xMap.keys())
    
    plt.legend(loc=2)
    plt.xlabel('median_Staerkeertrag[g/plant] %s' % year, fontsize=18)
    plt.ylabel('CV_Staerkeertrag[g/plant] %s' % year, fontsize=18)
    # plt.setp(plt.xticks()[1], rotation=90)    
    plt.subplots_adjust(bottom=0.14)
    
    plt.savefig('CV_yield_vs_med_yield_%s.svg' % year)
    plt.savefig('CV_yield_vs_med_yield_%s.png' % year)
    # plt.show()
    pass




def main(argv):
    
    reader = csv.reader(open(argv[0], 'rb'), delimiter=',', quotechar='"')
    X = map(float, [row[9] for row in reader][1:])
    reader = csv.reader(open(argv[1], 'rb'), delimiter=',', quotechar='"')
    Y = map(float, [row[9] for row in reader][1:])
    plot_yieldCV_yieldCV(X, Y, 'red')
    
    reader = csv.reader(open(argv[0], 'rb'), delimiter=',', quotechar='"')
    XY = map(lambda x:tuple(map(float,x)), [row[8:10] for row in reader][1:])
    x, y = zip(*XY)
    plot_yieldCV_yieldmedian(x, y, 'red', '2011')
    
    reader = csv.reader(open(argv[1], 'rb'), delimiter=',', quotechar='"')
    XY = map(lambda x:tuple(map(float,x)), [row[8:10] for row in reader][1:])
    x, y = zip(*XY)
    plot_yieldCV_yieldmedian(x, y, 'red', '2012')
    
    #print X
    #print Y
    #print len(X), len(Y)
    
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
