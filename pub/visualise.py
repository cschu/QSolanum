#!/usr/bin/env python
'''
Created on Mar 20, 2014

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''

GREY_STATION = {'Fassberg': {'markersize': 5, 'marker': 's', 'color': '0.4'},
                'MPI': {'markersize': 5, 'marker': 'o', 'color': '0.8'},
                'JKI': {'markersize': 5, 'marker': '^', 'color': '0.6'},
                'jkiShelter2011': {'markersize': 5, 'marker': 's', 'color': '0.4'}, 
                'jkiShelter2012': {'markersize': 5, 'marker': 'o', 'color': '0.8'},
                'pruef1': {'markersize': 5, 'marker': 's', 'color': '0.4'}, 
                'pruef2': {'markersize': 5, 'marker': '^', 'color': '0.6'}, 
                'pruef3': {'markersize': 5, 'marker': 'o', 'color': '0.8'}}



def add_plot(fig, heatsum, vpd, figfn, figtitle, stations, floweringTimes, 
             suffix='v1', subplot=511, figlabel='A', greyscale=GREY_STATION, 
             xlabel='', ylabel='', percentage_multiplier=1.0):
    
    maxY, minY = None, None
    max2Y, min2Y = None, None
    X, Y = [], []    
    plots = []

    try:
        ax = fig.add_subplot(subplot)
    except:
        ax = fig.add_subplot(*subplot)
    fontsize = 11
    ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
    
    if subplot == 322 or subplot == 324:            
        ax.set_xlim([0, 1450])
        if subplot == 324:
            ax.set_ylim([0, 1.5])
            ax.text(1300, 1.3, figlabel, weight='bold', fontsize=14)
        else:
            ax.set_ylim([0, 3.8])
            ax.text(1300, 3.25, figlabel, weight='bold', fontsize=14)
    elif subplot in (311, 312, 313):
        ax.set_ylim([0, 0.5])
        ax.set_xlim([200, 1400])
        ax.text(1700, 0.8, figlabel, weight='bold', fontsize=14)
    elif (subplot > 500 and subplot < 529) or (subplot in (331, 332, 333, 334, 335, 337, 338)):
        ax.set_ylim([0, 0.5 * percentage_multiplier])
        ax.set_xlim([200, 1400])
        ax.text(1275, 42.5, figlabel, weight='bold', fontsize=14)
    elif subplot >= 529 or subplot in (336, 339):
        ax.set_ylim([0, 1.0 * percentage_multiplier])
        ax.set_xlim([200, 1400])
        ax.text(1275, 85, figlabel, weight='bold', fontsize=14)
    else:
        ax.set_ylim([0, 2.8])    
        ax.set_xlim([0, 1650])
        ax.text(1485.7142857142856, 2.5, figlabel, weight='bold', fontsize=14)    
    
    for station in set(heatsum.keys()).intersection(set(vpd.keys())):    
        X, Y = [], []        
        linewidth = 2.0

        if station not in heatsum or station not in vpd:
            continue
        
        label = station
        if label == 'Fassberg':
            label = 'LWK'

        days = set(heatsum[station].keys()).intersection(set(vpd[station].keys()))
        
        try:
            if station[1] == 'drought':
                linewidth = 1.0
        except:
            pass

        try:
            floweringDay = floweringTimes[station]
        except:
            floweringDay = floweringTimes[station[0]]


        Y_sorted = []
        for day in sorted(days):
            print day, heatsum[station][day], vpd[station][day]
            if day == floweringDay:                
                plots.append(ax.plot(X, Y, linestyle='dashed', 
                                     linewidth=linewidth, **greyscale[station]))
                Y_sorted.extend(Y[:-1])
                X, Y = X[-1:], Y[-1:] 
            X.append(heatsum[station][day])
            Y.append(vpd[station][day] * percentage_multiplier)
        
        
        Y_sorted = sorted(Y + Y_sorted)
        max2Y, maxY = Y_sorted[-2:]
        minY, min2Y = Y_sorted[:2]
            
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(11)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(11)

        plots.append(ax.plot(X, Y, linestyle='solid', 
                             linewidth=linewidth, **greyscale[station]))        

        subplot_info = (subplot, station, max2Y, maxY, minY, min2Y)
        print 'Subplot %i Station %s MAX_VPD=%f,%f MIN_VPD=%f,%f' % subplot_info            

    plt.subplots_adjust(bottom=0.14)    
    pass
