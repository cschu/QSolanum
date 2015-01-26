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

import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np

import curves
import climatestuff as climate
from visualise import add_plot

DATAPATH='/home/schudoma/projects/trost/climate/sensor'

SENSOR_SOURCE = {'44443': [os.path.join(DATAPATH,
                                        'logger2_2011_05_19-2012_01_18.calibration.txt')],
                 '48656': [os.path.join(DATAPATH,
                                        'logger1_2011_04_12-2012_12_06.calibration.txt'),
                           os.path.join(DATAPATH,
                                        'logger2_2011_05_19-2012_01_18.calibration.txt')], #16-8 - 28-10
                 '51790': [os.path.join(DATAPATH,
                                        'logger2_2011_05_19-2012_01_18.calibration.txt'),
                           os.path.join(DATAPATH,
                                        'logger2_2012_01_26-2012_06_18.calibration.txt')],
                 '56575': [os.path.join(DATAPATH,
                                        'logger2_2012_01_26-2012_06_18.calibration.txt')],
                 '56726': [os.path.join(DATAPATH,
                                        'logger1_2011_04_12-2012_12_06.calibration.txt')],
                 '58243': [os.path.join(DATAPATH,
                                        'logger2_2012_07_02-2013_02_09.calibration.txt')],
                 '60319': [os.path.join(DATAPATH,
                                        'logger1_2012_12_06-2013_05_07.calibration.txt'),
                           os.path.join(DATAPATH,
                                        'logger2_2012_07_02-2013_02_09.calibration.txt')], #24-10 - 24-1
                 '62030': [os.path.join(DATAPATH,
                                        'logger1_2012_12_06-2013_05_07.calibration.txt')],
                 '62326': [os.path.join(DATAPATH,
                                        'logger1_2013_05_17-2013_08_14.calibration.txt')],
                 '56875': [],
                 '62327': []}

SENSOR_INFO = {(2011, 'MPI'): os.path.join(DATAPATH, 'sensor_44443.csv'),
               (2012, 'MPI'): os.path.join(DATAPATH, 'sensor_56726.csv'),
               (2013, 'MPI'): os.path.join(DATAPATH, 'sensor_62326.csv'),
               'pruef1': os.path.join(DATAPATH, 'sensor_56575.csv'),
               'pruef2': os.path.join(DATAPATH, 'sensor_58243.csv'),
               'pruef3': os.path.join(DATAPATH, 'sensor_60319.csv'),
               'pruef4': os.path.join(DATAPATH, 'sensor_62030.csv'),
               (2012, 'JKI'): os.path.join(DATAPATH, 'jkifield_sensor_56875_2012.csv'),
               (2013, 'JKI'): os.path.join(DATAPATH, 'jkifield_sensor_62327_2013.csv')}

# JKI Feld 2012: 56875 2013: 62327  # later ><;

SENSOR_PERIODS = {'44443': (datetime.datetime.strptime('2011-05-19', '%Y-%m-%d'), 
                            datetime.datetime.strptime('2011-08-16', '%Y-%m-%d')),
                  '48656': (datetime.datetime.strptime('2011-08-16', '%Y-%m-%d'), 
                            datetime.datetime.strptime('2011-10-28', '%Y-%m-%d')),
                  '51790': (datetime.datetime.strptime('2011-11-16', '%Y-%m-%d'), 
                            datetime.datetime.strptime('2012-02-10', '%Y-%m-%d')),                  
                  '56575': (datetime.datetime.strptime('2012-03-12', '%Y-%m-%d'), 
                            datetime.datetime.strptime('2012-06-01', '%Y-%m-%d')),
                  '56726': (datetime.datetime.strptime('2012-05-23', '%Y-%m-%d'), 
                            datetime.datetime.strptime('2012-07-30', '%Y-%m-%d')),
                  '58243': (datetime.datetime.strptime('2012-07-02', '%Y-%m-%d'), 
                            datetime.datetime.strptime('2012-09-28', '%Y-%m-%d')),
                  '60319': (datetime.datetime.strptime('2012-10-24', '%Y-%m-%d'), 
                            datetime.datetime.strptime('2013-01-24', '%Y-%m-%d')),
                  '62030': (datetime.datetime.strptime('2013-02-19', '%Y-%m-%d'), 
                            datetime.datetime.strptime('2013-05-07', '%Y-%m-%d')),
                  '62326': (datetime.datetime.strptime('2013-05-17', '%Y-%m-%d'), 
                            datetime.datetime.strptime('2013-08-14', '%Y-%m-%d')),
                  '56875': (datetime.datetime.strptime('2012-05-15', '%Y-%m-%d'), 
                            datetime.datetime.strptime('2012-08-29', '%Y-%m-%d')),
                  '62327': (datetime.datetime.strptime('2013-05-24', '%Y-%m-%d'), 
                            datetime.datetime.strptime('2013-08-29', '%Y-%m-%d'))                  
                  }

SAND_CURVE = curves.sandLogY
PEAT_CURVE = curves.peatLogY
SUBSTRATE_CURVE= {'44443': SAND_CURVE,
                  '48656': PEAT_CURVE,
                  '51790': PEAT_CURVE,
                  '56575': PEAT_CURVE,
                  '56726': SAND_CURVE,
                  '58243': PEAT_CURVE,
                  '60319': PEAT_CURVE,
                  '62030': PEAT_CURVE,
                  '62326': SAND_CURVE}

GREYSCALE = {2011: {'markersize': 5, 'marker': 's', 'color': '0.4'},
             2012: {'markersize': 5, 'marker': 'o', 'color': '0.8'},
             2013: {'markersize': 5, 'marker': '^', 'color': '0.6'},
             (2011, 'drought'): {'markersize': 5, 'marker': '', 'color': '0.5'},
             (2012, 'drought'): {'markersize': 5, 'marker': '', 'color': '0.5'},
             (2013, 'drought'): {'markersize': 5, 'marker': '', 'color': '0.5'},
             (2011, 'control'): {'markersize': 5, 'marker': '', 'color': '0.5'},
             (2012, 'control'): {'markersize': 5, 'marker': '', 'color': '0.5'},
             (2013, 'control'): {'markersize': 5, 'marker': '', 'color': '0.5'},
             ('pruef1', 'drought'): {'markersize': 5, 'marker': '', 'color': '0.5'},
             ('pruef2', 'drought'): {'markersize': 5, 'marker': '', 'color': '0.5'},
             ('pruef3', 'drought'): {'markersize': 5, 'marker': '', 'color': '0.5'},
             ('pruef4', 'drought'): {'markersize': 5, 'marker': '', 'color': '0.5'},
             ('pruef1', 'control'): {'markersize': 5, 'marker': '', 'color': '0.5'},
             ('pruef2', 'control'): {'markersize': 5, 'marker': '', 'color': '0.5'},
             ('pruef3', 'control'): {'markersize': 5, 'marker': '', 'color': '0.5'},
             ('pruef4', 'control'): {'markersize': 5, 'marker': '', 'color': '0.5'}}




def median(list_):
    list_.sort()
    p = len(list_)/2
    if len(list_) % 2 == 1:
        return list_[p]
    else:
        return sum(list_[p-1:p+1]) / 2.0

def std(list_):
    x_ = np.mean(list_)
    return math.sqrt(sum([(x - x_)**2 for x in list_])/float(len(list_)))

def read_logger_info(fn):
    # from file: sensor_$experimentID.csv
    # loggerID = int(os.path.basename(fn).replace('logger', '')[0])

    data = []
    reader = csv.reader(open(fn, 'rb'), delimiter=',', quotechar='"')
    header = reader.next()
    for row in reader:
        row = row
        data.append(dict(zip(header, row)))
        # data[-1]['loggerID'] = loggerID
    return data

def read_sensor_data(fn, channels, experimentID):
    temp_data = {c: {} for c in channels}
    time_data = {c: {} for c in channels}    
    
    with open(fn, 'rb') as fi:
        insane, total = 0, 0
        header = fi.readline().strip().split()        
        
        for line in fi:            
            line = line.strip().replace('" "', 'NULL')            
            data = dict(zip(header, re.split(' +', line)))
            sdate, stime = data['Date_Time'].split('_')             
            sensordate = map(int, sdate.split('.'))            
            sensordate = '20%02i-%02i-%02i' % (sensordate[2], sensordate[1], sensordate[0])
            
            for c in channels:
                total += 1
                try:
                    sensortime, sensortemp = float(data['S%iM' % c[0]]), float(data['S%iT' % c[0]])
                except:                    
                    continue
                if not re.match('1[0-4]', stime):
                    # ignore any reading from outside the 10am-2pm interval
                    continue
                if sensortime > 550.0 or sensortemp > 30.0:
                    # ignore high temperature or high time readings 
                    print 'INSANITY', sensortime, sensortemp
                    insane += 1
                    continue
                temp_data[c][sensordate] = temp_data[c].get(sensordate, []) + [sensortemp]
                rwc = curves.searchX(sensortime, SUBSTRATE_CURVE[experimentID])
                time_data[c][sensordate] = time_data[c].get(sensordate, []) + [rwc] 
                # time_data[c][sensordate] = time_data[c].get(sensordate, []) + [sensortime] 
            pass

    print total, insane        
    return time_data

def read_jki_sensor_data(fn):
    reader = csv.reader(open(fn, 'rb'), delimiter=',', quotechar='"')
    treatment = [cell.split()[0] for cell in reader.next()[2:]]
    channels = map(int, [cell[1:] for cell in reader.next()[2:]])
    reader.next()

    temp_data = {c: {} for c in channels}
    relH_data = {c: {} for c in channels}    


    total, insane = 0, 0
    for row in reader:
        sdate, stime = row[:2]
        # print 'SDATE', sdate
        sensordate = map(int, sdate.split('/'))
        
        sensordate = '%4i-%02i-%02i' % (sensordate[2], sensordate[0], sensordate[1])
        data = zip(channels, row, treatment)

        for i in xrange(0, len(data), 2):
            total += 1
            try:
                sensorRelHumidity, sensortemp = float(data[i][1])/100., float(data[i+1][1])
            except:
                continue
            if not re.match('1[0-4]', stime):
                # ignore any reading from outside the 10am-2pm interval
                continue
            if sensortemp > 30.0:
                # ignore high temperature or high time readings 
                print 'INSANITY', sensorRelHumidity, sensortemp
                insane += 1
                continue
            
            c = data[i][0]
            temp_data[c][sensordate] = temp_data[c].get(sensordate, []) + [sensortemp]           
            relH_data[c][sensordate] = relH_data[c].get(sensordate, []) + [sensorRelHumidity] 
        pass

    control_tdata_daily, drought_tdata_daily = {}, {}
    for c, t in zip(channels, treatment):
        for sd in relH_data[c]:
            med = np.median(relH_data[c][sd])
            if t == 'stress':
                drought_tdata_daily[sd] = drought_tdata_daily.get(sd, []) + [med]
            else:
                control_tdata_daily[sd] = control_tdata_daily.get(sd, []) + [med]

    for sd in control_tdata_daily:
        control_tdata_daily[sd] = (np.mean(control_tdata_daily[sd]))#, std(control_tdata_daily[sd]))   
        pass
    for sd in drought_tdata_daily:
        drought_tdata_daily[sd] = (np.mean(drought_tdata_daily[sd]))#, std(drought_tdata_daily[sd]))
        pass


    print total, insane
    return control_tdata_daily, drought_tdata_daily






def process_data(fname):
    logger_info = read_logger_info(fname)
    experimentID = os.path.basename(fname).replace('sensor_', '').replace('.csv', '')
    startD, endD = SENSOR_PERIODS[experimentID][:2]
    channels = [(int(linfo['Kanal_ID']), linfo['Logger']) for linfo in logger_info]
    time_data = {c: {} for c in channels}
    for fn in SENSOR_SOURCE[experimentID]:
        tdata = read_sensor_data(fn, channels, experimentID)
        for c in tdata:
            for sd in tdata[c]:
                sd_dt = datetime.datetime.strptime(sd, '%Y-%m-%d')
                if sd_dt >= startD and sd_dt <= endD:
                    # only store values from the growth period
                    if sd not in time_data[c]:
                        time_data[c][sd] = []
                    time_data[c][sd].extend(tdata[c][sd])

    #
    drought = [linfo for linfo in logger_info if linfo['Treatment'].strip() == 'drought']
    control = [linfo for linfo in logger_info if linfo['Treatment'].strip() == 'control']
    
    tmt_table = dict([((int(linfo['Kanal_ID'].strip()), linfo['Logger']), linfo['Treatment'].strip())
                      for linfo in logger_info])

    # compute daily median (10am-2pm) sensor readings for each channel
    control_tdata_daily, drought_tdata_daily = {}, {}
    for c in channels:
        for sd in time_data[c]:#[sd]:
            med = np.median(time_data[c][sd])
            if tmt_table[c] == 'drought':
                drought_tdata_daily[sd] = drought_tdata_daily.get(sd, []) + [med]
            else:
                control_tdata_daily[sd] = control_tdata_daily.get(sd, []) + [med]
    
    # for each treatment, compute mean, std of daily median between all channels
    for sd in control_tdata_daily:
        control_tdata_daily[sd] = (np.mean(control_tdata_daily[sd]))#, std(control_tdata_daily[sd]))   
    for sd in drought_tdata_daily:
        drought_tdata_daily[sd] = (np.mean(drought_tdata_daily[sd]))#, std(drought_tdata_daily[sd]))

    return control_tdata_daily, drought_tdata_daily

def compute_SWC_per_week(swc):
    swc_per_week = {}
    for k in swc:
        week = tuple(map(int, datetime.datetime.strftime(datetime.datetime.strptime(k, '%Y-%m-%d'), '%Y-%W').split('-')))        
        swc_per_week[week] = swc_per_week.get(week, []) + [swc[k]]
        print swc_per_week
    return {week: sum(swc_per_week[week])/float(len(swc_per_week[week])) 
            for week in swc_per_week}


def main(argv):

    plt.rc('text', usetex=True)
    plt.rcParams['text.latex.preamble']=[r"\usepackage{amsmath}"]
    
    plt.rc('xtick', labelsize=14)#, fontweight='bold')
    plt.rc('ytick', labelsize=14)#, fontweight='bold')
    rcParams['figure.figsize'] = (8.27, 12)[::-1]
    rcParams['figure.dpi'] = 600
    font = {'family' : 'serif',
            'weight' : 'bold',
            'size'   : 12}
    plt.rc('font', **font)
    
    plt.setp(plt.xticks()[1], rotation=90)
    plt.subplots_adjust(bottom=0.20)
    plt.tight_layout()

    figure = plt.figure(1)
    # figure.suptitle("Soil Water Content vs Heatsum\n%s" % "Academic field and greenhouse trials")
    plt.axis('off')


    ff = climate.filter_by_date
    groupedTemperatures, maxTemperatures, minTemperatures = {}, {}, {}
    rawTemperatures, rawRelHumidities = {}, {} 
    floweringTimes = {}
    sensorReadings = {}
    
    figfn = 'MPIFIELD'
    figtitle = 'FIGTITLE'
    figlabels = ['A', 'B', 'C']
    sp_offset = 1
    for year in [2011, 2012, 2013]:        
        start, floweringTimes[year], end = climate.FIELD_TRIALS[(year, 'MPI')]
        floweringTimes[year] = climate.computeFloweringWeek(floweringTimes[year])
        rawTemperatures[year], stuff = map(lambda x:ff(x, start_date=start, end_date=end),
                                           climate.read_mpi_climate_data(climate.mpi_climate[year]))
        groupedTemperatures[year] = climate.pack_ungrouped_data(rawTemperatures[year], key=0)
        maxTemperatures[year], minTemperatures[year] = (
            climate.aggregate_values_from_grouped(groupedTemperatures[year], max),
            climate.aggregate_values_from_grouped(groupedTemperatures[year], min))

        sensorReadings[year] = process_data(SENSOR_INFO[(year, 'MPI')])
        SWC, HEATSUM = {}, {}

        """SWC[(year, 'control')] = compute_SWC_per_week(sensorReadings[year][0])
        SWC[(year, 'drought')] = compute_SWC_per_week(sensorReadings[year][1])
        hsum = climate.compute_heatsum_per_week(climate.compute_heatsum_per_day(
                maxTemperatures[year], minTemperatures[year]))
        HEATSUM[(year, 'control')], HEATSUM[(year, 'drought')] = hsum, hsum
        """
        SWC = {(year, 'control'): sensorReadings[year][0],
               (year, 'drought'): sensorReadings[year][1]}
        hsum = climate.compute_heatsum_per_day(maxTemperatures[year], minTemperatures[year])
        HEATSUM = {(year, 'control'): hsum, (year, 'drought'): hsum}
        
        subplot = 330 + sp_offset # 520 + sp_offset
        sp_offset += 1 # sp_offset += 2
        add_plot(figure, HEATSUM, SWC, figfn, figtitle, [year],
                 floweringTimes, suffix='', subplot=subplot, figlabel=figlabels.pop(0),
                 greyscale=GREYSCALE,
                 xlabel='Heatsum [$\mathbf{^\circ}\mathbf{C_{cumul}}$]', 
                 ylabel='SWC [$\mathbf{\%nFC}$]',
                 percentage_multiplier=100.0)
        



    # MPI greenhouse trials
    groupedTemperatures, maxTemperatures, minTemperatures = {}, {}, {}
    rawTemperatures, rawRelHumidities = {}, {} 
    floweringTimes = {}
    sensorReadings = {}

    rawTemperatures['GolmCGW'], stuff = climate.read_mpi_climate_data(climate.golm_cgw)
    sp_offset = 2
    subplots = [334, 335, 337, 338]
    figlabels = ['D', 'E', 'G', 'H']
    figfn='MPICGW'
    for trial, tdata in sorted(climate.CGW_TRIALS.items()):
        floweringTimes[trial] = climate.computeFloweringWeek(tdata[1])
        rawTemperatures[trial] = ff(rawTemperatures['GolmCGW'], start_date=tdata[0], end_date=tdata[2])
        groupedTemperatures[trial] = climate.pack_ungrouped_data(rawTemperatures[trial], key=0)
        maxTemperatures[trial], minTemperatures[trial] = (
            climate.aggregate_values_from_grouped(groupedTemperatures[trial], max),
            climate.aggregate_values_from_grouped(groupedTemperatures[trial], min))
        sensorReadings[trial]= process_data(SENSOR_INFO[trial])
        SWC, HEATSUM = {}, {}
        """SWC[(trial, 'control')] = compute_SWC_per_week(sensorReadings[trial][0])
        SWC[(trial, 'drought')] = compute_SWC_per_week(sensorReadings[trial][1])
        hsum = climate.compute_heatsum_per_week(climate.compute_heatsum_per_day(
                maxTemperatures[trial], minTemperatures[trial]))
        HEATSUM[(trial, 'control')], HEATSUM[(trial, 'drought')] = hsum, hsum"""
        SWC = {(trial, 'control'): sensorReadings[trial][0],
               (trial, 'drought'): sensorReadings[trial][1]}
        hsum = climate.compute_heatsum_per_day(maxTemperatures[trial], minTemperatures[trial])
        HEATSUM = {(trial, 'control'): hsum, (trial, 'drought'): hsum}

        subplot = subplots.pop(0)# 520 + sp_offset

        add_plot(figure, HEATSUM, SWC, figfn, figtitle, [trial],
                 floweringTimes, suffix='', subplot=subplot, figlabel=figlabels.pop(0),
                 greyscale=GREYSCALE,
                 xlabel='Heatsum [$\mathbf{^\circ}\mathbf{C_{cumul}}$]', 
                 ylabel='SWC [$\mathbf{\%nFC}$]',
                 percentage_multiplier=100.0)
        
        sp_offset += 2
        pass
    
    # JKI field trials
    groupedTemperatures, maxTemperatures, minTemperatures = {}, {}, {}
    rawTemperatures, rawRelHumidities = {}, {} 
    floweringTimes = {}
    sensorReadings = {}

    figlabels = ['F', 'I']
    sp_offset = 9
    subplots = [336, 339]
    for year in [2012, 2013]:
        start, floweringTimes[year], end = climate.FIELD_TRIALS[(year, 'JKI')]
        floweringTimes[year] = climate.computeFloweringWeek(floweringTimes[year])
        rawTemperatures[year], stuff = map(lambda x:ff(x, start_date=start, end_date=end),
                                           climate.read_jki_climate_data(climate.jki_climate[year]))
        groupedTemperatures[year] = climate.pack_ungrouped_data(rawTemperatures[year], key=0)
        maxTemperatures[year], minTemperatures[year] = (
            climate.aggregate_values_from_grouped(groupedTemperatures[year], max),
            climate.aggregate_values_from_grouped(groupedTemperatures[year], min))
        
        sensorReadings[year] = read_jki_sensor_data(SENSOR_INFO[(year, 'JKI')])
         
        SWC, HEATSUM = {}, {}  
        """SWC[(year, 'control')] = compute_SWC_per_week(sensorReadings[year][0])
        SWC[(year, 'drought')] = compute_SWC_per_week(sensorReadings[year][1])
        hsum = climate.compute_heatsum_per_week(climate.compute_heatsum_per_day(
                maxTemperatures[year], minTemperatures[year]))
        HEATSUM[(year, 'control')], HEATSUM[(year, 'drought')] = hsum, hsum"""
        SWC = {(year, 'control'): sensorReadings[year][0],
               (year, 'drought'): sensorReadings[year][1]}
        hsum = climate.compute_heatsum_per_day(maxTemperatures[year], minTemperatures[year])
        HEATSUM = {(year, 'control'): hsum, (year, 'drought'): hsum}
        
        
        subplot = subplots.pop(0) # (5,2,0 + sp_offset)
        add_plot(figure, HEATSUM, SWC, figfn, figtitle, [year],
                 floweringTimes, suffix='', subplot=subplot, figlabel=figlabels.pop(0),
                 greyscale=GREYSCALE,
                 xlabel='Heatsum [$\mathbf{^\circ}\mathbf{C_{cumul}}$]', 
                 ylabel='Rel Soil Moisture [$\%$]',
                 percentage_multiplier=100.0)
        # ylabel='SWC [$\mathbf{\%nFC}$]')
        
        sp_offset += 1
        
        
        


    


    figure.savefig("swc_heatsum_alltrials_3x3.png")
    pass


if __name__ == '__main__': main(sys.argv[1:])
