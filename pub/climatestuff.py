#!/usr/bin/env python
'''
Created on Nov 19, 2013

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import math
import time
import datetime

import numpy as np

"""
TRIAL DATES: planting date, flowering date, termination date
"""
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
                (2011, 'Fassberg'): ('2011-04-11', '2011-06-04', '2011-09-02'),
                (2012, 'Fassberg'): ('2012-04-16', '2012-06-11', '2012-09-04'),
                (2013, 'Fassberg'): ('2013-04-20', '2013-06-11', '2013-09-19')}

"""
CLIMATE DATA
"""
DATAPATH='/home/schudoma/projects/trost/climate/weather_2013'
    
jki_shelter = [os.path.join(DATAPATH, 'jkishelter_climate_45990_2011.csv'), 
               os.path.join(DATAPATH, 'jkishelter_climate_57803_2012.csv')]
golm_cgw = os.path.join(DATAPATH, 'golm_climate_cgw.csv')
mpi_climate = {2011: os.path.join(DATAPATH, 'golm_climate_44443_2011.csv'),
               2012: os.path.join(DATAPATH, 'golm_climate_56726_2012.csv'),
               2013: os.path.join(DATAPATH, 'golm_climate_62326_2013.csv')}
jki_climate = {2012: os.path.join(DATAPATH, 'jkifield_climate_56875_2012_A.csv'),
               2013: os.path.join(DATAPATH, 'jkifield_climate_62327_2013_A.csv')}

"""
DATA INPUT
"""
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



def filter_by_date(data, start_date='2011-01-01', end_date='2013-12-01'):
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    return {k: data[k] for k in data
            if start <= datetime.datetime.strptime(k[0], '%Y-%m-%d').date() and  
            datetime.datetime.strptime(k[0], '%Y-%m-%d').date() <= end}

def computeFloweringWeek(floweringDate):
    Ymd = floweringDate.split('-')
    print '[cFW]:', floweringDate
    return (int(Ymd[0]), 
            int(datetime.datetime.strftime(datetime.datetime.strptime(floweringDate, '%Y-%m-%d'), '%W')))

def pack_ungrouped_data(ungrouped, key=None):
    grouped = {}    
    for k in ungrouped:
        grouped[k[key]] = grouped.get(k[key], []) + ungrouped[k] 
    return grouped
    
def aggregate_values_from_grouped(grouped, criterion_func):
    return {k: criterion_func(grouped[k]) for k in grouped}     
    
def get_values_according_to_criterion(data, criterion_func, verbose=False):
    for k in data:
        for kk in data[k]:
            if verbose:
                print k, kk, sorted(data[k][kk]), criterion_func(data[k][kk])
            data[k][kk] = criterion_func(data[k][kk])
    return data



def calc_VPD(T_Celsius, relHumidity):
    
    #print T_Celsius, relHumidity
    
    T = T_Celsius + 273.15 # T_Kelvin
    PSI_IN_KPA = 6.8948
    
    # according to http://en.wikipedia.org/wiki/Vapour_Pressure_Deficit
    A, B, C, D, E, F = -1.88e4, -13.1, -1.5e-2, 8e-7, -1.69e-11, 6.456    
    vp_sat = math.exp(A / T + B + C * T + D * T ** 2 + E * T ** 3 + F * math.log(T))    
    # according to http://ohioline.osu.edu/aex-fact/0804.html
    A, B, C, D, E, F = -1.044e4, -1.129e1, -2.702e-2, 1.289e-5, -2.478e-9, 6.456
    vp_sat = math.exp(A / T + B + C * T + D * T ** 2 + E * T ** 3 + F * math.log(T)) * PSI_IN_KPA    
    # according to 
    # http://physics.stackexchange.com/questions/4343/how-can-i-calculate-vapor-pressure-deficit-from-temperature-and-relative-humidit
    vp_sat = 6.11 * math.exp((2.5e6 / 461) * (1 / 273 - 1 / (273 + T)))    
    # according to Licor LI-6400 manual pg 14-10
    # and Buck AL (1981) New equations for computing vapor pressure and enhancement factor. J Appl Meteor 20:1527-1532
    vp_sat = 0.61365 * math.exp((17.502 * T_Celsius) / (240.97 + T_Celsius))
    
    vp_air = vp_sat * relHumidity
    return vp_sat - vp_air # or vp_sat * (1 - relHumidity)

def compute_VPD_per_hour(temperatures, relHumidity):
    return {timepoint: calc_VPD(temperatures[timepoint], relHumidity[timepoint])
            for timepoint in set(temperatures.keys()).intersection(set(relHumidity.keys()))}
    

def compute_weekly_vpd(temperatures, relHumidity, station):
    print '[CWVPD: %s]' % station        
    hourly = {timepoint: calc_VPD(temperatures[timepoint][0], relHumidity[timepoint][0])
              for timepoint in set(temperatures.keys()).intersection(set(relHumidity.keys()))}
    # print hourly
    # print 'XXX'

    daily = {}
    midday = (datetime.datetime.strptime('10:00:00', '%H:%M:%S'),
              datetime.datetime.strptime('14:00:00', '%H:%M:%S'))
    for tp in hourly:
        print tp
        try:
            hour = datetime.datetime.strptime(tp[1], '%H:%M:%S')        
        except:
            hour = datetime.datetime.strptime(tp[1], '%H:%M')        
        if midday[0] <= hour <= midday[1]:
            daily[tp[0]] = daily.get(tp[0], []) + [hourly[tp]]
    # print daily
    # sys.exit(1)

    weekly = {}
    """
    for k in sorted(hourly):
        week = tuple(map(int, datetime.datetime.strftime(datetime.datetime.strptime(k[0], '%Y-%m-%d'), '%Y-%W').split('-')))
        weekly[week] = weekly.get(week, []) + [float(hourly[k])]
    """
    for k in sorted(daily):
        week = tuple(map(int, datetime.datetime.strftime(datetime.datetime.strptime(k, '%Y-%m-%d'), '%Y-%W').split('-')))
        weekly[week] = weekly.get(week, []) + [np.median(daily[k])]

    print weekly
    return {week: sum(weekly[week])/len(weekly[week]) for week in weekly}



    
    
def compute_VPD_per_day(temperatures, relHumidity):
    return {day: calc_VPD(temperatures[day], relHumidity[day])
            for day in set(temperatures.keys()).intersection(set(relHumidity.keys()))}
    
def compute_VPD_per_week(vpd):
    vpd_per_week = {}
    for k in vpd:
        week = tuple(map(int, datetime.datetime.strftime(datetime.datetime.strptime(k, '%Y-%m-%d'), '%Y-%W').split('-')))
        vpd_per_week[week] = vpd_per_week.get(week, []) + [vpd[k]]    
    return {week: sum(vpd_per_week[week])/float(len(vpd_per_week[week])) for week in vpd_per_week}

def calc_heat_sum(tmin, tmax, tbase=6.0):
    """
    Daily heat summation is defined as:
    heat_sum_d = max(tx - tbase, 0), with    
    tx = (tmin + tmax)/2 and
    tmax = min(tmax_measured, 30.0) 
    """
    tmax = min(tmax, 30.0)
    tx = (tmin + tmax) / 2.0
    return max(tx - tbase, 0.0)

def compute_heatsum_per_day(maxTemps, minTemps):
    heatsum, heatsum_day = 0, {}
    for k in sorted(set(maxTemps.keys()).intersection(set(minTemps.keys()))):
        heatsum += calc_heat_sum(minTemps[k], maxTemps[k])
        heatsum_day[k] = heatsum        
    return heatsum_day

def compute_heatsum_per_week(heatsum_day, day=5):
    heatsum_week = {} 
    for k in heatsum_day:        
        year, week, weekday = map(int, datetime.datetime.strftime(datetime.datetime.strptime(k, '%Y-%m-%d'), '%Y %W %w').split())
        if weekday == day:
            heatsum_week[(year, week)] = heatsum_day[k]
    return heatsum_week



class ClimateData(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        pass
    @classmethod
    def fromGolmFieldData(class_, data):
        data = {'temperature': float(data[0]),
                'humidity': float(data[1]),
                'lightIntensity': float(data[2]),
                'windVelocity': float(data[3]),
                'precipitation': float(data[4])}        
        return class_(data)    
    pass




def main(argv):
    
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
