#!/usr/bin/env python
'''
Created on Oct 24, 2013

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import re
import csv
import math
import datetime
import argparse

import numpy as np
import matplotlib.pyplot as plt
from BeautifulSoup import BeautifulStoneSoup as BSS

import climatestuff as climate
import login
TROST_DB = login.get_db(db='trost_prod')

"""
this converts JKI field climate data (temp, rH) into JKI shelter climate data (rH, temp)
such that both data files can be processed by the same function 
tail -n +2  jkifield_climate_56875_2012.csv | cut -f 1,2,5,6 -d , | sed 's/"//g' | sed 's/\(^[0-3][0-9]\)\.\([01][0-9]\)\.\(201[23]\)/\2\/\1\/\3/g' | sed 's/,\([-0-9.]\+\),\([0-9.]\+$\)/,\2,\1/g' > jkifield_climate_56875_2012_A.csv
"""

STATIONS = {'Fassberg': 'b-s', 'Potsdam': 'r-*', 'Tribsees': 'k-+', 
            'MPI': 'g-o', 'JKI': 'k-^',
            'jkiShelter2011': 'b-s', 'jkiShelter2012': 'r-^',
            'pruef1': 'b-o', 'pruef2': 'r-s', 'pruef3': 'k-^'}

CGW_TRIALS = {'pruef1': ('2012-02-29', '2012-04-01', '2012-06-01'), 
              'pruef2': ('2012-06-27', '2012-08-01', '2012-10-02'),
              'pruef3': ('2012-10-17', '2012-11-20', '2013-01-24')}
JKI_SHELTER_TRIALS = {'jkiShelter2011': ('2011-05-13', '2011-06-23', '2011-08-15'),
                      'jkiShelter2012': ('2012-06-01', '2012-06-22', '2012-08-09')}
FIELD_TRIALS = {(2011, 'MPI'): ('2011-04-01', '2011-06-03', '2011-09-13'),
                (2012, 'MPI'): ('2012-04-01', '2012-06-01', '2012-08-28'),
                (2013, 'MPI'): ('2013-04-01', '2013-06-13', '2013-08-20'),                
                (2012, 'JKI'): ('2012-04-01', '2012-06-18', '2012-08-28'),
                (2013, 'JKI'): ('2013-04-01', '2013-06-19', '2013-09-19'),
                (2011, 'Fassberg'): ('2011-04-11', '2011-06-04', '2011-09-02'),
                (2012, 'Fassberg'): ('2012-04-16', '2012-06-11', '2012-09-04'),
                (2013, 'Fassberg'): ('2013-04-20', '2013-06-11', '2013-09-19')}




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
    


def read_mpi_climate_data(fn, start_date='-01-01', end_date='-12-01', use_datetime=True):
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

def plot_rawdata(data, year, station, datatype, suffix='v1'):
    X, Y = [], []
   
    fig = plt.figure()
    fig.suptitle("%s (%i) - %s" % (station, year, datatype[0]))
    ax = fig.add_subplot(111)
    ax.set_xlabel("Time") #, fontsize=6)
    ax.set_ylabel("%s %s" % datatype)
    
    sept_1 = []
    for k, v in sorted(data.items()):
        X.append(k)
        #if k.strip().endswith('-09-01'):
        if '-09-' in k.strip():
            sept_1.append((k, len(X) - 1))
        Y.append(v)
        
    Xpos = [i+1 for i,x in enumerate(X)]
        
    ax.plot(Xpos, Y, 'b*')
    ax.plot(Xpos, Y, 'c-', linewidth=0.5)
    
    # ax.plot([sept_1[0][1] + 1], [0], 'ro')
    ax.axvline(x=sept_1[0][1] + 1, ymin=0, ymax=1, color='r', linewidth='0.3')
    
    # P.arrow( x, y, dx, dy, **kwargs )
    """
    ax.arrow(sept_1[0][1] + 1, 0, 0, -10, fc='r', ec='k', 
             head_width=10, head_length=10)
    
    ax.annotate("",
            xy=(sept_1[0][1] + 1, 0), xycoords='data',
            xytext=(sept_1[0][1], 10), textcoords='data',
            arrowprops=dict(arrowstyle="->",
                            connectionstyle="arc3"),
            )
    
    ax.annotate("Test",
            xy=(1,1), xycoords='data',
            xytext=(2,2), textcoords='data',
            size=20, va="center", ha="center",
            arrowprops=dict(arrowstyle="simple",
                            connectionstyle="arc3,rad=-0.2"), 
            )
    """
    # labels = [item.get_text() for item in ax.get_xticklabels()]
    ax.set_xticks(Xpos)
    ax.set_xticklabels(X)
    #plt.xticks(np.arange(0, len(xlabels)), xlabels)
    fig.savefig("%s.%i.%s.%s.png" % (station, year, datatype[0].lower(), suffix))
    pass
    


def generate_plots(heatsum, vpd, figfn, figtitle, stations, floweringTimes, suffix='v1'):
    X, Y = [], []
    
    fig = plt.figure()
    fig.suptitle("VPD vs Heatsum\n%s" % figtitle)
    ax = fig.add_subplot(111)
    ax.set_xlabel('Heatsum [$\mathbf{^\circ}\mathbf{C_{cumul}}$]', fontsize=14, fontweight='bold')
    ax.set_ylabel('Vapour Pressure Deficit [$\mathbf{kPa}$]', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 2.5])    
    ax.set_xlim([0, 1650])
    plots = []
    
    """
    if not year is None:
        week_sep1 = (int(year), int(datetime.datetime.strftime(datetime.datetime.strptime('%s-09-01' % year, '%Y-%m-%d'), '%W')))
    """
    
    print 'bloom', floweringTimes
    
    for station in set(heatsum.keys()).intersection(set(vpd.keys())):    
        print 'STATION', station, stations
        if station not in heatsum or station not in vpd:
            print station, 'URGH!'
            continue
        
        print 'HS', heatsum[station]
        print 'VPD', vpd[station]
        
        label = station
        if label == 'Fassberg':
            label = 'LWK'
        X, Y = [], []        
        for day in sorted(heatsum[station]):
            print day, heatsum[station][day], vpd[station][day]
            if day == floweringTimes[station]:                 
                plots.append(ax.plot(X, Y, stations[station].replace('-', '--'), 
                                     label='%s - before Flowering' % label, linewidth=2.0))
                X, Y = X[-1:], Y[-1:] 
            X.append(heatsum[station][day])
            Y.append(vpd[station][day])
            
        plots.append(ax.plot(X, Y, stations[station], label='%s - after Flowering' % label, linewidth=2.0))
        
        """
        for day in sorted(heatsum[station]):
            print day, heatsum[station][day], vpd[station][day]
            X.append(heatsum[station][day])
            Y.append(vpd[station][day])
            
        plots.append(ax.plot(X, Y, stations[station], label=label))
        plots.append(ax.axvline(x=heatsum[station][floweringTimes[station]], ymin=0, ymax=1, 
                                color=stations[station][0], linewidth='0.3',
                                label='%s_beginFlowering' % station))
        """
        """
        if not year is None:
            plots.append(ax.axvline(x=heatsum[station][week_sep1], ymin=0, ymax=1, color=stations[station][0], linewidth='0.3',
                                    label='%s_Sep' % station))
        """
        
    # ax.legend(loc=1, fontsize=14)
    
    #ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=8,
    #          ncol=2, mode="expand", borderaxespad=0.)
    
    #ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., mode="expand", fontsize=8)
    
    plt.subplots_adjust(bottom=0.14)
    
    fig.savefig("vpd_heatsum_%s.%s.png" % (figfn, suffix))
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
    

def main(argv):
    argparser = argparse.ArgumentParser(description='Process TROST station climate data.')
    argparser.add_argument('--year', action='store', help='One of the three TROST1 years [2011, 2012, 2013].')
    argparser.add_argument('--dwd_temperatures', action='store', dest='dwd_temperatures', 
                           help='DWD station temperature hourly values if local data is unavailable.')
    argparser.add_argument('--dwd_humidities', action='store', dest='dwd_humidities',
                           help='DWD station rel. humidity hourly values if local data is unavailable.')
    argparser.add_argument('--mpi_climate', action='store', dest='mpi_climate',
                           help='MPI station data.')
    argparser.add_argument('--jki_climate', action='store', dest='jki_climate',
                           help='JKI station [UniRostock] data.')
    argparser.add_argument('--jki_shelter', action='store', nargs=2)
    argparser.add_argument('--golm_cgw', action='store')
    argparser.add_argument('--version', action='store')    
    
    args = argparser.parse_args(argv)    
    print args
    
    plt.rc('text', usetex=True)
    plt.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
    
    plt.rc('xtick', labelsize=14)#, fontweight='bold')
    plt.rc('ytick', labelsize=14)#, fontweight='bold')
    plt.setp(plt.xticks()[1], rotation=90)
    plt.subplots_adjust(bottom=0.14)
    font = {'family' : 'serif',
            'weight' : 'bold',
            'size'   : 14}
    plt.rc('font', **font)
    
    
    if True: #args.year == 2011:
        del STATIONS['Tribsees']
        del STATIONS['Potsdam']
            
    groupedTemperatures, maxTemperatures, minTemperatures = {}, {}, {}
    rawTemperatures, rawRelHumidities = {}, {} 
    floweringTimes = {}
    
    if not args.jki_shelter is None:        
        for i, td in enumerate(sorted(JKI_SHELTER_TRIALS.items())):
            rawTemperatures[td[0]], rawRelHumidities[td[0]] = read_jki_climate_data(args.jki_shelter[i])
            rawTemperatures[td[0]] = filter_by_date(rawTemperatures[td[0]], start_date=td[1][0], end_date=td[1][2])
            floweringTimes[td[0]] = computeFloweringWeek(JKI_SHELTER_TRIALS[td[0]][1])                              
        figtitle = 'JKI Shelter Trials 2011/2012'
        figfn = 'jki_shelter'
    elif not args.golm_cgw is None:
        rawTemperatures['GolmCGW'], rawRelHumidities['GolmCGW'] = read_mpi_climate_data(args.golm_cgw)
        for trial, tdata in CGW_TRIALS.items():            
            rawTemperatures[trial] = filter_by_date(rawTemperatures['GolmCGW'], start_date=tdata[0], end_date=tdata[2])
            rawRelHumidities[trial] = filter_by_date(rawRelHumidities['GolmCGW'], start_date=tdata[0], end_date=tdata[2])
            floweringTimes[trial] = computeFloweringWeek(tdata[1])                                
        figtitle = 'MPI CGW Trials 2012/2013'
        figfn = 'mpi_cgw'
    else: # field trials
        rawTemperatures = read_XML(args.dwd_temperatures, STATIONS)
        rawRelHumidities = get_values_according_to_criterion(read_XML(args.dwd_humidities, STATIONS),
                                                         lambda x:map(lambda y:y/100.0, x))
        figtitle = 'Academia Field Trials %s' % args.year
        figfn = args.year
                    
    print '>>>', STATIONS.keys(), rawTemperatures.keys()    
    for station in set(STATIONS.keys()).intersection(set(rawTemperatures.keys())):
        if not args.year is None: 
            
            key = (int(args.year), str(station))
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
    
    ff = filter_by_date
    if not args.mpi_climate is None:    
        key = (int(args.year), 'MPI')
        print 'FT[key]:', key, FIELD_TRIALS[key]
        start, floweringTimes['MPI'], end = FIELD_TRIALS[key]#[0], FIELD_TRIALS[key][2]
        floweringTimes['MPI'] = computeFloweringWeek(floweringTimes['MPI'])
        rawTemperatures['MPI'], rawRelHumidities['MPI'] = map(lambda x:ff(x, start_date=start, end_date=end), 
                                                              read_mpi_climate_data(args.mpi_climate))
        groupedTemperatures['MPI'] = pack_ungrouped_data(rawTemperatures['MPI'], key=0)        
        maxTemperatures['MPI'], minTemperatures['MPI'] = (aggregate_values_from_grouped(groupedTemperatures['MPI'], max),
                                                            aggregate_values_from_grouped(groupedTemperatures['MPI'], min))
    if not args.jki_climate is None:
        key = (int(args.year), 'JKI')
        start, floweringTimes['JKI'], end = FIELD_TRIALS[key]#[0], FIELD_TRIALS[key][2]
        print 'JKIFT:', floweringTimes['JKI'], 'key=', key
        floweringTimes['JKI'] = computeFloweringWeek(floweringTimes['JKI'])

        rawTemperatures['JKI'], rawRelHumidities['JKI'] = map(lambda x:ff(x, start_date=start, end_date=end),
                                                              read_jki_climate_data(args.jki_climate))
        groupedTemperatures['JKI'] = pack_ungrouped_data(rawTemperatures['JKI'], key=0)
        maxTemperatures['JKI'], minTemperatures['JKI'] = (aggregate_values_from_grouped(groupedTemperatures['JKI'], max),
                                                          aggregate_values_from_grouped(groupedTemperatures['JKI'], min))
    
    VPD = {station: climate.compute_weekly_vpd(rawTemperatures[station], rawRelHumidities[station], station) 
           for station in set(rawTemperatures.keys()).intersection(set(rawRelHumidities.keys()))}
    HEATSUM = {station: climate.compute_heatsum_per_week(climate.compute_heatsum_per_day(maxTemperatures[station], 
                                                                                         minTemperatures[station]))
               for station in set(maxTemperatures.keys()).intersection(set(minTemperatures.keys()))}
    
    generate_plots(HEATSUM, VPD, figfn, figtitle, STATIONS, floweringTimes, suffix=args.version)        
    pass

if __name__ == '__main__': main(sys.argv[1:])
