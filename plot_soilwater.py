#!/usr/bin/env python
'''
Created on Jul 25, 2013

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys

import csv

import matplotlib.pyplot as plt
import numpy as np

def main(argv):
    
    def isnumber(x):
        try:
            x = float(x)
        except:
            return False
        return True
    
    xlabels = []
    line_labels = range(40)
    data = []
    with open(argv[0]) as csvfile:
        reader = csv.reader(csvfile, delimiter='\t', quotechar='"')
        for row in reader:
            xlabels.append(row[0].split('_')[0])
            data.append(map(lambda x:float(x) if isnumber(x) else None, row[1:]))
    data_t = np.array(data).transpose()
    
    plots = []
    fig = plt.figure()
    fig.suptitle(argv[1])
    ax = plt.subplot(1,1,1)
    for i, row in enumerate(data_t):
        style = 'r-'
        lwidth = 0.5
        if i < 3:
            style = 'b-'
            lwidth = 1.5                
        ax.plot(range(len(xlabels)), row, style, label=str(i), linewidth=lwidth)
    
    plt.xticks(np.arange(0, len(xlabels)), xlabels)
    #ax.set_xticklabels(xlabels)
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Sensor Output [unit]', fontsize=18)
    
    
    plt.setp(plt.xticks()[1], rotation=90)
    
    plt.subplots_adjust(bottom=0.14)
    
    plt.savefig(argv[2])
    
    
    
    
    handles, labels = ax.get_legend_handles_labels()
    
    # ax.legend(handles, labels, ncol=4, loc=8)
    # plt.show() 
    
    
            
    
    
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
