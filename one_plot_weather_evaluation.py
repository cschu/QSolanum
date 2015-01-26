#!/usr/bin/env python
'''
Created on Oct 24, 2013

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import os
import re
import csv
import math
import datetime
import argparse
from itertools import cycle



import numpy as np
import matplotlib.pyplot as plt
from BeautifulSoup import BeautifulStoneSoup as BSS

import climatestuff as climate
#import login
from matplotlib import rcParams
#TROST_DB = login.get_db(db='trost_prod')

"""
this converts JKI field climate data (temp, rH) into JKI shelter climate data (rH, temp)
such that both data files can be processed by the same function 
tail -n +2  jkifield_climate_56875_2012.csv | cut -f 1,2,5,6 -d , | sed 's/"//g' | sed 's/\(^[0-3][0-9]\)\.\([01][0-9]\)\.\(201[23]\)/\2\/\1\/\3/g' | sed 's/,\([-0-9.]\+\),\([0-9.]\+$\)/,\2,\1/g' > jkifield_climate_56875_2012_A.csv
"""

# Heike:
DETHLINGEN_STATION = 'Soltau' # 'Fassberg'
DATAPATH = '.' #/home/schudoma/projects/trost/climate/weather_2013'

STATIONS = {DETHLINGEN_STATION: 'b-s', 'Potsdam': 'r-*', 'Tribsees': 'k-+', 
            'MPI': 'g-o', 'JKI': 'k-^', 
            'jkiShelter2011': 'b-s', 'jkiShelter2012': 'r-^',
            'pruef1': 'b-o', 'pruef2': 'r-s', 'pruef3': 'k-^'}
del STATIONS['Tribsees']
del STATIONS['Potsdam']

GREY_STATION = {DETHLINGEN_STATION: {'markersize': 5, 'marker': 's', 'color': '0.4'},
                'Soltau': {'markersize': 5, 'marker': 's', 'color': '0.4'},
                'MPI': {'markersize': 5, 'marker': 'o', 'color': '0.8'},
                'JKI': {'markersize': 5, 'marker': '^', 'color': '0.6'},
                'jkiShelter2011': {'markersize': 5, 'marker': 's', 'color': '0.4'}, 
                'jkiShelter2012': {'markersize': 5, 'marker': 'o', 'color': '0.8'},
                'pruef1': {'markersize': 5, 'marker': 's', 'color': '0.4'}, 
                'pruef2': {'markersize': 5, 'marker': '^', 'color': '0.6'}, 
                'pruef3': {'markersize': 5, 'marker': 'o', 'color': '0.8'}}


CGW_TRIALS = {'pruef1': ('2012-02-29', '2012-04-01', '2012-06-01'), 
              'pruef2': ('2012-06-27', '2012-08-01', '2012-10-02'),
              'pruef3': ('2012-10-17', '2012-11-20', '2013-01-24'),
              'pruef4': ('2013-02-13', '2013-03-21', '2013-05-16')} 
JKI_SHELTER_TRIALS = {'jkiShelter2011': ('2011-05-13', '2011-06-23', '2011-08-15'),
                      'jkiShelter2012': ('2012-06-01', '2012-06-22', '2012-08-09')}
FIELD_TRIALS = {(2011, 'MPI'): ('2011-04-01', '2011-06-03', '2011-09-13'),
                (2012, 'MPI'): ('2012-04-01', '2012-06-01', '2012-08-28'),
                (2013, 'MPI'): ('2013-04-01', '2013-06-13', '2013-08-20'),                
                (2012, 'JKI'): ('2012-04-01', '2012-06-18', '2012-08-28'),
                (2013, 'JKI'): ('2013-04-01', '2013-06-19', '2013-09-19'),
                (2011, DETHLINGEN_STATION): ('2011-04-11', '2011-06-04', '2011-09-02'),
                (2012, DETHLINGEN_STATION): ('2012-04-16', '2012-06-11', '2012-09-04'),
                (2013, DETHLINGEN_STATION): ('2013-04-20', '2013-06-11', '2013-09-19')}


    
jki_shelter = [os.path.join(DATAPATH, 'jkishelter_climate_45990_2011.csv'), 
               os.path.join(DATAPATH, 'jkishelter_climate_57803_2012.csv')]
golm_cgw = os.path.join(DATAPATH, 'golm_climate_cgw.csv')
mpi_climate = {2011: os.path.join(DATAPATH, 'golm_climate_44443_2011.csv'),
               2012: os.path.join(DATAPATH, 'golm_climate_56726_2012.csv'),
               2013: os.path.join(DATAPATH, 'golm_climate_62326_2013.csv')}
jki_climate = {2012: os.path.join(DATAPATH, 'jkifield_climate_56875_2012_A.csv'),
               2013: os.path.join(DATAPATH, 'jkifield_climate_62327_2013_A.csv')}





def read_jki_climate_data(fn, start_date='-01-01', end_date='-12-01'):
    #5/13/2011,10:36:45,48,24.2,57,22.6 <- shelter: 1 or 2 temp/rH pairs    
    #1/1/2012,0:00:00,99.3,1.9 <- field: 1 temp/rH pair
    reader = csv.reader(open(fn, 'rb'), delimiter=',', quotechar='"')
    relHumidity, temperature = {}, {}
    
    for row in reader:
        date_, time_ = row[0:2]
        try:
            values = map(float, row[2:])
        except:
            continue
        mdY = map(int, date_.split('/'))
        date_ = '%4i-%02i-%02i' % (mdY[2], mdY[0], mdY[1])
        year = str(mdY[2])
        start = datetime.datetime.strptime(year + start_date, '%Y-%m-%d').date()
        end = datetime.datetime.strptime(year + end_date, '%Y-%m-%d').date()
        day = datetime.datetime.strptime(date_, '%Y-%m-%d').date()
        
        if day >= start and day <= end:         
            key = (date_, time_)            
            rH, temp = map(lambda x:x/100.0, values[0:1]), map(float, values[1:2])
            try:
                rH.append(values[2] / 100.0)
                temp.append(float(values[3]))
            except:
                pass
                        
            relHumidity[key] = relHumidity.get(key, []) + [sum(rH) / len(rH)]
            temperature[key] = temperature.get(key, []) + [sum(temp) / len(temp)]
        pass
        
    return temperature, relHumidity
    


def read_mpi_climate_data(fn, start_date='-01-01', end_date='-12-31', use_datetime=True):
    reader = csv.reader(open(fn, 'rb'), delimiter='\t', quotechar='"')
    relHumidity, temperature = {}, {}
    
    for row in reader:               
        date_, time_ = str(row[0]).split()
        try:
            values = map(float, row[1:])
        except:
            continue
        dmY = date_.split('.')
        date_ = '%s-%s-%s' % tuple(dmY[::-1])        
        year = dmY[2]
        start = datetime.datetime.strptime(year + start_date, '%Y-%m-%d').date()
        end = datetime.datetime.strptime(year + end_date, '%Y-%m-%d').date()
        day = datetime.datetime.strptime(date_, '%Y-%m-%d').date()        
        
        if day >= start and day <= end:         
            if use_datetime:
                key = (date_, time_)
            else:
                key = date_
            relHumidity[key] = relHumidity.get(key, []) + [values[1] / 100.0]
            temperature[key] = temperature.get(key, []) + [float(values[0])]
        pass
        
    return temperature, relHumidity
    

def read_XML(fn, stations, start_date='-04-01', end_date='-09-30', use_datetime=True):
    station_data = {}
    raw = open(fn).read()
    raw = re.sub('> [ ]+<', '><', raw.replace('\n', ''))
    soup = BSS(raw)
    soup_data = soup.data
    station = soup_data.stationname
    
    while True:
        if station is None: 
            break
        station_name = station.get('value')
        if station_name in stations:
            station_data[station_name] = {}
        
            datapoint = station.v
            while True:
                if datapoint is None:
                    break
                v_value = float(datapoint.text)
            
                date_, time_ = str(datapoint.get('date')), None
                if 'T' in date_:
                    date_, time_ = [value.strip('Z') for value in date_.split('T')]
                year = date_.split('-')[0]
                start = datetime.datetime.strptime(year + start_date, '%Y-%m-%d').date()
                end = datetime.datetime.strptime(year + end_date, '%Y-%m-%d').date()
                day = datetime.datetime.strptime(date_, '%Y-%m-%d').date()
                if day >= start and day <= end:
                    if use_datetime:
                        key = (date_, time_)
                    else:
                        key = date_
                    station_data[station_name][key] = station_data[station_name].get(key, []) + [v_value]                
                datapoint = datapoint.nextSibling
        
        station = station.nextSibling 
        pass
    
    return station_data



def median(list_):
    list_.sort()
    p = len(list_)/2
    if len(list_) % 2 == 1:
        return list_[p]
    else:
        return sum(list_[p-1:p+1]) / 2.0
    


def add_plot(fig, heatsum, vpd, figfn, figtitle, stations, floweringTimes, suffix='v1', subplot=511, figlabel='A', greyscale=GREY_STATION, xlabel='', ylabel='', percentage_multiplier=1.0):
    
    grey_linestyles = cycle(map(lambda tu:dict(zip(('color','dashes'),tu)),
                                (('0.5',(4,1,1,1)),
                                 ('0.4',(2,1)),
                                 ('0.3',(5,1,2,1)),
                                 ('0.2',(4,1)),
                                 ('0.1',(6,1)),
                                 ('0.0',(10,1)),
                                 ('0.0',(20,1)))))

    """
    class IsotoProfileFigure(Figure):
     def __init__(self, *args, **kwargs):
         self.linestyles = grey_linestyles

     def plot(self, gases, label='_nolegend'):
         style = self.linestyles.next() #TODO: allow for usual style  
    modifiers passed in
         self.isoaxis.plot(deltas,self.verts,label=label, **style) 
    """
    maxY, minY = None, None
    max2Y, min2Y = None, None
    X, Y = [], []    
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
            #ax.set_ylim([0, 2.5])
            ax.set_ylim([0, 3.8])
            # ax.text(1300, 2.166666666666667, figlabel, weight='bold', fontsize=14)
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
        # ax.set_ylim([0, 1.5])    
        ax.set_ylim([0, 2.8])    
        ax.set_xlim([0, 1650])
        # ax.text(1485.7142857142856, 1.3, figlabel, weight='bold', fontsize=14)
        ax.text(1485.7142857142856, 2.5, figlabel, weight='bold', fontsize=14)
    plots = []
    
    # print 'bloom', floweringTimes
    
    for station in set(heatsum.keys()).intersection(set(vpd.keys())):    
        print 'STATION', station, stations
        if station not in heatsum or station not in vpd:
            print station, 'URGH!'
            continue
        
        print 'HS', sorted(heatsum[station].items())
        print 'VPD', sorted(vpd[station].items())
        
        label = station
        if label == DETHLINGEN_STATION:
            label = 'LWK'
        X, Y = [], []        
        # for day in sorted(heatsum[station]):
        days = set(heatsum[station].keys()).intersection(set(vpd[station].keys()))
        
        linewidth = 2.0
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
            if day == floweringDay: #floweringTimes[station]:                 
                #plots.append(ax.plot(X, Y, stations[station].replace('-', '--'), 
                #                     label='%s - before Flowering' % label, linewidth=2.0))
                
                plots.append(ax.plot(X, Y, linestyle='dashed', linewidth=linewidth, **greyscale[station]))
                Y_sorted.extend(Y[:-1])
                X, Y = X[-1:], Y[-1:] 
            X.append(heatsum[station][day])
            Y.append(vpd[station][day] * percentage_multiplier)
        
        
        Y_sorted = sorted(Y + Y_sorted)
        #if maxY == None:
        max2Y, maxY = Y_sorted[-2:]
        minY, min2Y = Y_sorted[:2]
        #else:
        #    max2Y, maxY = sorted([maxY, max2Y] + Y_sorted[-2:])[-2:]
        #    minY, min2Y = sorted([minY, min2Y] + Y_sorted[:2])[:2]

            
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(11)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(11)
            
        
        
        #plots.append(ax.plot(X, Y, stations[station], label='%s - after Flowering' % label, linewidth=2.0))
        plots.append(ax.plot(X, Y, linestyle='solid', linewidth=linewidth, **greyscale[station]))        
        print 'Subplot %i Station %s MAX_VPD=%f,%f MIN_VPD=%f,%f' % (subplot, station, max2Y, maxY, minY, min2Y)

    plt.subplots_adjust(bottom=0.14)    
    pass

def pack_ungrouped_data(ungrouped, key=None):
    grouped = {}    
    for k in ungrouped:
        grouped[k[key]] = grouped.get(k[key], []) + ungrouped[k] 
    return grouped

def get_values_according_to_criterion(data, criterion_func, verbose=False):
    for k in data:
        for kk in data[k]:
            if verbose:
                print k, kk, sorted(data[k][kk]), criterion_func(data[k][kk])
            data[k][kk] = criterion_func(data[k][kk])
    return data

def aggregate_values_from_grouped(grouped, criterion_func):
    return {k: criterion_func(grouped[k]) for k in grouped}     

def filter_by_date(data, start_date='2011-01-01', end_date='2013-12-01'):
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    return {k: data[k] for k in data
            if start <= datetime.datetime.strptime(k[0], '%Y-%m-%d').date() and  
            datetime.datetime.strptime(k[0], '%Y-%m-%d').date() <= end}
    
def computeFloweringWeek(floweringDate):
    Ymd = floweringDate.split('-')
    print '[cFW]:', floweringDate
    return (int(Ymd[0]), int(datetime.datetime.strftime(datetime.datetime.strptime(floweringDate, '%Y-%m-%d'), '%W')))
    
    
def do_something(rawTemperatures, rawRelHumidities, groupedTemperatures, 
                 maxTemperatures, minTemperatures, year, floweringTimes):
    for station in set(STATIONS.keys()).intersection(set(rawTemperatures.keys())):
        if not year is None:            
            key = (int(year), str(station))
            print 'key ?=', key
            start, floweringTimes[str(station)], end = FIELD_TRIALS[key]#[0], FIELD_TRIALS[key][2]
            
            try:                
                floweringTimes[str(station)] = computeFloweringWeek(floweringTimes[str(station)])
            except:
                print 'BLOOM-boom:', floweringTimes[str(station)]
                continue
            rawTemperatures[station] = filter_by_date(rawTemperatures[station], start_date=start, end_date=end)
            rawRelHumidities[station] = filter_by_date(rawRelHumidities[station], start_date=start, end_date=end)
        
        groupedTemperatures[station] = pack_ungrouped_data(rawTemperatures[station], key=0)
        maxTemperatures[station] = aggregate_values_from_grouped(groupedTemperatures[station], max)
        minTemperatures[station] = aggregate_values_from_grouped(groupedTemperatures[station], min)

        for k in sorted(maxTemperatures[station]):
            print station, k, maxTemperatures[station][k], minTemperatures[station][k]

        pass
    

def main(argv):
    
    plt.rc('text', usetex=True)
    plt.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
    
    plt.rc('xtick', labelsize=14)#, fontweight='bold')
    plt.rc('ytick', labelsize=14)#, fontweight='bold')
    rcParams['figure.figsize'] = 8.27, 11.69
    rcParams['figure.dpi'] = 600
    font = {'family' : 'serif',
            'weight' : 'bold',
            'size'   : 14}
    plt.rc('font', **font)
    
    plt.setp(plt.xticks()[1], rotation=90)
    plt.subplots_adjust(bottom=0.14)

    figure = plt.figure(1)#, figsize=(1024, 768), dpi=600)
    #figure.suptitle("Vapour Pressure Deficit [VPD] vs Heatsum\n%s" % "Academic field and greenhouse trials")
    plt.axis('off')
    
    ff = filter_by_date
    groupedTemperatures, maxTemperatures, minTemperatures = {}, {}, {}
    rawTemperatures, rawRelHumidities = {}, {} 
    floweringTimes = {}
    
    sp_row = 1
    
    for year, figlabel in [(2011, 'A'), (2012, 'C'), (2013, 'E')]:
        groupedTemperatures, maxTemperatures, minTemperatures = {}, {}, {}
        rawTemperatures, rawRelHumidities = {}, {} 
        floweringTimes = {}
        dwd_temperatures = 'temperatures_%i_academia.XML' % year 
        rawTemperatures = read_XML(os.path.join(DATAPATH, dwd_temperatures), STATIONS)
        rawRelHumidities = get_values_according_to_criterion(read_XML(os.path.join(DATAPATH, 'relHumidity_%i_academia.XML' % year), STATIONS),
                                                             lambda x:map(lambda y:y/100.0, x))
        figtitle = 'Academia Field Trials %s' % year
        figfn = year
        do_something(rawTemperatures, rawRelHumidities, groupedTemperatures, maxTemperatures, minTemperatures, year, floweringTimes)
        
        key = (int(year), 'MPI')
        print 'FT[key]:', key, FIELD_TRIALS[key]
        start, floweringTimes['MPI'], end = FIELD_TRIALS[key]
        floweringTimes['MPI'] = computeFloweringWeek(floweringTimes['MPI'])
        rawTemperatures['MPI'], rawRelHumidities['MPI'] = map(lambda x:ff(x, start_date=start, end_date=end), 
                                                              read_mpi_climate_data(mpi_climate[year]))
        groupedTemperatures['MPI'] = pack_ungrouped_data(rawTemperatures['MPI'], key=0)        
        maxTemperatures['MPI'], minTemperatures['MPI'] = (aggregate_values_from_grouped(groupedTemperatures['MPI'], max),
                                                          aggregate_values_from_grouped(groupedTemperatures['MPI'], min))
        if year != 2011:
            
            key = (int(year), 'JKI')
            start, floweringTimes['JKI'], end = FIELD_TRIALS[key]
            print 'JKIFT:', floweringTimes['JKI'], 'key=', key
            floweringTimes['JKI'] = computeFloweringWeek(floweringTimes['JKI'])
            rawTemperatures['JKI'], rawRelHumidities['JKI'] = map(lambda x:ff(x, start_date=start, end_date=end),
                                                                  read_jki_climate_data(jki_climate[year]))
            groupedTemperatures['JKI'] = pack_ungrouped_data(rawTemperatures['JKI'], key=0)
            maxTemperatures['JKI'], minTemperatures['JKI'] = (aggregate_values_from_grouped(groupedTemperatures['JKI'], max),
                                                              aggregate_values_from_grouped(groupedTemperatures['JKI'], min))

        
        
        VPD = {station: climate.compute_weekly_vpd(rawTemperatures[station], rawRelHumidities[station], station) 
               for station in set(rawTemperatures.keys()).intersection(set(rawRelHumidities.keys()))}
        HEATSUM = {station: climate.compute_heatsum_per_week(climate.compute_heatsum_per_day(maxTemperatures[station], 
                                                                                             minTemperatures[station]))
                   for station in set(maxTemperatures.keys()).intersection(set(minTemperatures.keys()))}        
        
        add_plot(figure, HEATSUM, VPD, figfn, figtitle, STATIONS, floweringTimes, suffix='', subplot=320 + sp_row, figlabel=figlabel, xlabel='Heatsum [$\mathbf{^\circ}\mathbf{Cd}$]', ylabel='VPD [$\mathbf{kPa}$]')
        sp_row += 2
        
        
        print '====>'

        for k in sorted(set(VPD[DETHLINGEN_STATION]).intersection(set(HEATSUM[DETHLINGEN_STATION]))):
            print k, HEATSUM[DETHLINGEN_STATION][k], VPD[DETHLINGEN_STATION][k]

        # sys.exit(1)

    

    groupedTemperatures, maxTemperatures, minTemperatures = {}, {}, {}
    rawTemperatures, rawRelHumidities = {}, {} 
    floweringTimes = {}
    
    for i, td in enumerate(sorted(JKI_SHELTER_TRIALS.items())):
        rawTemperatures[td[0]], rawRelHumidities[td[0]] = read_jki_climate_data(jki_shelter[i])
        rawTemperatures[td[0]] = filter_by_date(rawTemperatures[td[0]], start_date=td[1][0], end_date=td[1][2])
        floweringTimes[td[0]] = computeFloweringWeek(JKI_SHELTER_TRIALS[td[0]][1])                              
    figtitle = 'JKI Shelter Trials 2011/2012'
    figfn = 'jki_shelter'
    do_something(rawTemperatures, rawRelHumidities, groupedTemperatures, maxTemperatures, minTemperatures, None, floweringTimes)
    VPD = {station: climate.compute_weekly_vpd(rawTemperatures[station], rawRelHumidities[station], station) 
           for station in set(rawTemperatures.keys()).intersection(set(rawRelHumidities.keys()))}



    HEATSUM = {station: climate.compute_heatsum_per_week(climate.compute_heatsum_per_day(maxTemperatures[station], 
                                                                                         minTemperatures[station]))
               for station in set(maxTemperatures.keys()).intersection(set(minTemperatures.keys()))}
    
    
    add_plot(figure, HEATSUM, VPD, figfn, figtitle, STATIONS, floweringTimes, suffix='', subplot=322, figlabel='B', xlabel='Heatsum [$\mathbf{^\circ}\mathbf{Cd}$]', ylabel='VPD [$\mathbf{kPa}$]')
    sp_row += 1

    groupedTemperatures, maxTemperatures, minTemperatures = {}, {}, {}
    rawTemperatures, rawRelHumidities = {}, {} 
    floweringTimes = {}
        
    rawTemperatures['GolmCGW'], rawRelHumidities['GolmCGW'] = read_mpi_climate_data(golm_cgw)
    for trial, tdata in CGW_TRIALS.items():            
        rawTemperatures[trial] = filter_by_date(rawTemperatures['GolmCGW'], start_date=tdata[0], end_date=tdata[2])
        rawRelHumidities[trial] = filter_by_date(rawRelHumidities['GolmCGW'], start_date=tdata[0], end_date=tdata[2])
        floweringTimes[trial] = computeFloweringWeek(tdata[1])                                
    figtitle = 'MPI CGW Trials 2012/2013'
    figfn = 'mpi_cgw'
    do_something(rawTemperatures, rawRelHumidities, groupedTemperatures, maxTemperatures, minTemperatures, None, floweringTimes)
    VPD = {station: climate.compute_weekly_vpd(rawTemperatures[station], rawRelHumidities[station], station) 
           for station in set(rawTemperatures.keys()).intersection(set(rawRelHumidities.keys()))}
    HEATSUM = {station: climate.compute_heatsum_per_week(climate.compute_heatsum_per_day(maxTemperatures[station], 
                                                                                         minTemperatures[station]))
               for station in set(maxTemperatures.keys()).intersection(set(minTemperatures.keys()))}
    
    sp_row += 1
    add_plot(figure, HEATSUM, VPD, figfn, figtitle, STATIONS, floweringTimes, suffix='', subplot=324, figlabel='D', xlabel='Heatsum [$\mathbf{^\circ}\mathbf{Cd}$]', ylabel='VPD [$\mathbf{kPa}$]')
    
    
    
    figure.savefig("vpd_heatsum_alltrials_notitle.png")
        
    
            
    
        
    pass

if __name__ == '__main__': main(sys.argv[1:])