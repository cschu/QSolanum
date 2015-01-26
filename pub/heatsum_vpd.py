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

import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np
from BeautifulSoup import BeautifulStoneSoup as BSS

import climatestuff as climate
from visualise import add_plot

"""
STATION LIST AND VISUALIZATION PARAMETERS
"""
STATIONS = {'Fassberg': 'b-s', 
            'MPI': 'g-o', 'JKI': 'k-^',
            'jkiShelter2011': 'b-s', 'jkiShelter2012': 'r-^',
            'pruef1': 'b-o', 'pruef2': 'r-s', 'pruef3': 'k-^'}


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
    
    
def do_something(rawTemperatures, rawRelHumidities, groupedTemperatures, 
                 maxTemperatures, minTemperatures, year, floweringTimes):
    for station in set(STATIONS.keys()).intersection(set(rawTemperatures.keys())):
        if not year is None:            
            key = (int(year), str(station))
            start, floweringTimes[str(station)], end = climate.FIELD_TRIALS[key]
            
            try:                
                floweringTimes[str(station)] = climate.computeFloweringWeek(floweringTimes[str(station)])
            except:
                continue
            rawTemperatures[station] = climate.filter_by_date(rawTemperatures[station], 
                                                              start_date=start, end_date=end)
            rawRelHumidities[station] = climate.filter_by_date(rawRelHumidities[station], 
                                                               start_date=start, end_date=end)
        
        groupedTemperatures[station] = climate.pack_ungrouped_data(rawTemperatures[station], 
                                                                   key=0)
        maxTemperatures[station] = climate.aggregate_values_from_grouped(groupedTemperatures[station], max)
        minTemperatures[station] = climate.aggregate_values_from_grouped(groupedTemperatures[station], min)
        pass
    

def main(argv):
    
    plt.rc('text', usetex=True)
    plt.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
    
    plt.rc('xtick', labelsize=14)
    plt.rc('ytick', labelsize=14)
    rcParams['figure.figsize'] = 8.27, 11.69
    rcParams['figure.dpi'] = 600
    font = {'family' : 'serif',
            'weight' : 'bold',
            'size'   : 14}
    plt.rc('font', **font)
    
    plt.setp(plt.xticks()[1], rotation=90)
    plt.subplots_adjust(bottom=0.14)

    figure = plt.figure(1)
    plt.axis('off')
    
    ff = climate.filter_by_date
    groupedTemperatures, maxTemperatures, minTemperatures = {}, {}, {}
    rawTemperatures, rawRelHumidities = {}, {} 
    floweringTimes = {}
    
    sp_row = 1
    
    for year, figlabel in [(2011, 'A'), (2012, 'C'), (2013, 'E')]:
        groupedTemperatures, maxTemperatures, minTemperatures = {}, {}, {}
        rawTemperatures, rawRelHumidities = {}, {} 
        floweringTimes = {}
        dwd_temperatures = 'temperatures_%i_academia.XML' % year 
        rawTemperatures = read_XML(os.path.join(climate.DATAPATH, dwd_temperatures), STATIONS)
        rH_data = os.path.join(climate.DATAPATH, 'relHumidity_%i_academia.XML' % year)
        rawRelHumidities = climate.get_values_according_to_criterion(read_XML(rH_data, STATIONS),
                                                                     lambda x:map(lambda y:y/100.0, x))
        figtitle, figfn = 'Academia Field Trials %s' % year, year
        do_something(rawTemperatures, rawRelHumidities, groupedTemperatures, 
                     maxTemperatures, minTemperatures, year, floweringTimes)
        
        key = (int(year), 'MPI')
        print 'FT[key]:', key, climate.FIELD_TRIALS[key]
        start, floweringTimes['MPI'], end = climate.FIELD_TRIALS[key]
        floweringTimes['MPI'] = climate.computeFloweringWeek(floweringTimes['MPI'])
        rawTemperatures['MPI'], rawRelHumidities['MPI'] = map(lambda x:ff(x, start_date=start, end_date=end), 
                                                              climate.read_mpi_climate_data(climate.mpi_climate[year]))
        groupedTemperatures['MPI'] = climate.pack_ungrouped_data(rawTemperatures['MPI'], key=0)        
        maxTemperatures['MPI'], minTemperatures['MPI'] = (climate.aggregate_values_from_grouped(groupedTemperatures['MPI'], max),
                                                          climate.aggregate_values_from_grouped(groupedTemperatures['MPI'], min))
        if year != 2011:
            
            key = (int(year), 'JKI')
            start, floweringTimes['JKI'], end = climate.FIELD_TRIALS[key]#[0], FIELD_TRIALS[key][2]
            print 'JKIFT:', floweringTimes['JKI'], 'key=', key
            floweringTimes['JKI'] = climate.computeFloweringWeek(floweringTimes['JKI'])
            rawTemperatures['JKI'], rawRelHumidities['JKI'] = map(lambda x:ff(x, start_date=start, end_date=end),
                                                                  climate.read_jki_climate_data(climate.jki_climate[year]))
            groupedTemperatures['JKI'] = climate.pack_ungrouped_data(rawTemperatures['JKI'], key=0)
            maxTemperatures['JKI'], minTemperatures['JKI'] = (climate.aggregate_values_from_grouped(groupedTemperatures['JKI'], max),
                                                              climate.aggregate_values_from_grouped(groupedTemperatures['JKI'], min))

        
        
        VPD = {station: climate.compute_weekly_vpd(rawTemperatures[station], rawRelHumidities[station], station) 
               for station in set(rawTemperatures.keys()).intersection(set(rawRelHumidities.keys()))}
        HEATSUM = {station: climate.compute_heatsum_per_week(climate.compute_heatsum_per_day(maxTemperatures[station], 
                                                                                             minTemperatures[station]))
                   for station in set(maxTemperatures.keys()).intersection(set(minTemperatures.keys()))}        
        
        add_plot(figure, HEATSUM, VPD, figfn, figtitle, STATIONS, floweringTimes, suffix='', subplot=320 + sp_row, figlabel=figlabel, xlabel='Heatsum [$\mathbf{^\circ}\mathbf{Cd}$]', ylabel='VPD [$\mathbf{kPa}$]')
        sp_row += 2
        
    groupedTemperatures, maxTemperatures, minTemperatures = {}, {}, {}
    rawTemperatures, rawRelHumidities = {}, {} 
    floweringTimes = {}
    
    for i, td in enumerate(sorted(climate.JKI_SHELTER_TRIALS.items())):
        rawTemperatures[td[0]], rawRelHumidities[td[0]] = climate.read_jki_climate_data(climate.jki_shelter[i])
        rawTemperatures[td[0]] = filter_by_date(rawTemperatures[td[0]], start_date=td[1][0], end_date=td[1][2])
        floweringTimes[td[0]] = climate.computeFloweringWeek(climate.JKI_SHELTER_TRIALS[td[0]][1])                              
    figtitle = 'JKI Shelter Trials 2011/2012'
    figfn = 'jki_shelter'
    do_something(rawTemperatures, rawRelHumidities, groupedTemperatures, maxTemperatures, minTemperatures, None, floweringTimes)
    VPD = {station: climate.compute_weekly_vpd(rawTemperatures[station], rawRelHumidities[station], station) 
           for station in set(rawTemperatures.keys()).intersection(set(rawRelHumidities.keys()))}

    # sys.exit(1)

    HEATSUM = {station: climate.compute_heatsum_per_week(climate.compute_heatsum_per_day(maxTemperatures[station], 
                                                                                         minTemperatures[station]))
               for station in set(maxTemperatures.keys()).intersection(set(minTemperatures.keys()))}
    
    
    add_plot(figure, HEATSUM, VPD, figfn, figtitle, STATIONS, floweringTimes, suffix='', subplot=322, figlabel='B', xlabel='Heatsum [$\mathbf{^\circ}\mathbf{Cd}$]', ylabel='VPD [$\mathbf{kPa}$]')
    sp_row += 1

    groupedTemperatures, maxTemperatures, minTemperatures = {}, {}, {}
    rawTemperatures, rawRelHumidities = {}, {} 
    floweringTimes = {}
        
    rawTemperatures['GolmCGW'], rawRelHumidities['GolmCGW'] = climate.read_mpi_climate_data(climate.golm_cgw)
    for trial, tdata in climate.CGW_TRIALS.items():            
        rawTemperatures[trial] = filter_by_date(rawTemperatures['GolmCGW'], start_date=tdata[0], end_date=tdata[2])
        rawRelHumidities[trial] = filter_by_date(rawRelHumidities['GolmCGW'], start_date=tdata[0], end_date=tdata[2])
        floweringTimes[trial] = climate.computeFloweringWeek(tdata[1])                                
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
