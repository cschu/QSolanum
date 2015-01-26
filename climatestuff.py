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
# Datum_Uhrzeit  
# Raumtemperatur1 Raumfeuchte1    Innenlichtstaerke [umol/qms]1   
# Aussen Temperatur10     Aussen Feuchte10        Aussen Licht10  Aussen Windgeschwindigkeit10 Regen10

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
    #for k, v in sorted(temperatures.items()):
    #    print k, v
    #for k, v in sorted(relHumidity.items()):
    #    print k, v    
    # sys.exit(1)

    daily = {}
    midday = (datetime.datetime.strptime('10:00:00', '%H:%M:%S'),
              datetime.datetime.strptime('14:00:00', '%H:%M:%S'))
    for tp in hourly:
        # print 'TP', tp
        try:
            hour = datetime.datetime.strptime(tp[1], '%H:%M:%S')        
        except:
            hour = datetime.datetime.strptime(tp[1], '%H:%M')        
        if midday[0] <= hour <= midday[1]:
            daily[tp[0]] = daily.get(tp[0], []) + [hourly[tp]]

    # for d in sorted(daily): print d, daily[d]
    print 'DAILY', len(daily)
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

    print 'WEEKLY', len(weekly)
    for w in sorted(weekly): print w, weekly[w], sum(weekly[w])/len(weekly[w])

    

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
