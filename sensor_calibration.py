#!/usr/bin/env python
'''
Created on Oct 10, 2013

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import csv
import re

import matplotlib.pyplot as plt
import numpy as np


SENSOR_KEYS = {1: [(1, 12, 36), (1, 24, 48), (1, 30, 54)],
               2: [(1, 2, 34), (1, 5, 38), (1, 33, 57)],
               3: [(1, 6, 30), (1, 31, 55), (1, 34, 58)],
               4: [(1, 9, 33), (1, 18, 42), (1, 25, 49)],
               5: [(1, 4, 28), (1, 32, 56), (1, 3, 27)],
               6: [(1, 3, 27), (1, 20, 44), (1, 29, 53)]}

MAP_CHANNEL_POT = {12: 1, 24: 1, 30: 1, 2: 2, 5: 2, 33: 2, 6: 3, 31: 3, 34: 3,
                   9: 4, 18: 4, 25: 4, 1: 5, 4: 5, 32: 5, 3: 6, 20: 6, 29: 6}
CHANNEL_SUBSTRATES = {12: 'Sand', 24: 'Sand', 30: 'Sand', 2: 'Sand', 5: 'Sand', 33: 'Sand', 6: 'Sand', 31: 'Sand', 34: 'Sand',
                   9: 'Peat', 18: 'Peat', 25: 'Peat', 1: 'Peat', 4: 'Peat', 32: 'Peat', 3: 'Peat', 20: 'Peat', 29: 'Peat'}
CHANNEL_SYMBOLS = {12: '*', 24: 'x', 30: '.', 2: '*', 5: 'x', 33: '.', 6: '*', 31: 'x', 34: '.',
                   9: '*', 18: 'x', 25: '.', 1: '*', 4: 'x', 32: '.', 3: '*', 20: 'x', 29: '.'}

W_EMPTY_POT_SAND = 0.26866 #kg
W_EMPTY_POT_PEAT = 0.06208 #kg
DRY_FRACTION_PEAT = 0.5316
DRY_FRACTION_SAND = 1.0000


class Pot(object):    
    def __init__(self):
        pass
    def set_T0_weights(self, w_nosensor, w_sensor):
        self.w_sensor = w_sensor
        self.w_nosensor = w_nosensor        
        self.sensor_weight = w_sensor - w_nosensor
        self.w_drysubstrate = (w_nosensor - self.w_empty) * self.dry_fraction        
        pass
    def set_water_capacity(self, w_after_watering):
        self.water_capacity = w_after_watering - self.w_empty - self.w_drysubstrate - self.sensor_weight
        pass
    def calc_water_content(self, w_after_watering):
        awc = w_after_watering - self.w_empty - self.w_drysubstrate - self.sensor_weight
        rwc = awc / self.water_capacity
        return awc, rwc
    pass

class PeatPot(Pot):
    def __init__(self):
        Pot.__init__(self)
        self.w_empty = W_EMPTY_POT_PEAT
        self.dry_fraction = DRY_FRACTION_PEAT
        pass
    pass  

class SandPot(Pot):
    def __init__(self):
        Pot.__init__(self)
        self.w_empty = W_EMPTY_POT_SAND
        self.dry_fraction = DRY_FRACTION_SAND
        pass
    pass  

def read_potdata(fn):
    
    def is_float(x):
        try:
            x = float(x)
        except:
            return False
        return True
    
    pots = [SandPot(), SandPot(), SandPot(), PeatPot(), PeatPot(), PeatPot()]
    
    reader = csv.reader(open(fn, 'rb'), delimiter=',', quotechar='"')
    header = reader.next()
    T0_nosensor = map(float, reader.next()[2:8])
    T0_sensor = map(float, reader.next()[2:8])
    T1_water = map(float, reader.next()[2:8])
    
    for i, v in enumerate(zip(T0_nosensor, T0_sensor)):
        pots[i].set_T0_weights(v[0], v[1])
    for i, v in enumerate(T1_water):
        pots[i].set_water_capacity(v)
    
    rwc_data = {i: {} for i in xrange(6)}
    
    for row in reader:
        for i, v in enumerate(row[2:8]):
            awc, rwc = pots[i].calc_water_content(float(v)) if is_float(v) else (None, None)
            rwc_data[i][row[1]] = rwc
            
    return rwc_data


def read_sensor_data(fn, channels):
    temp_data = {c: {} for c in channels}
    time_data = {c: {} for c in channels}
    
    def median(list_):
        list_.sort()
        p = len(list_)/2
        if len(list_) % 2 == 1:
            return list_[p]
        else:
            return sum(list_[p-1:p+1]) / 2.0
    
    with open(fn, 'rb') as fi:
        header = fi.readline().strip().split()
        
        for line in fi:
            line = line.strip().replace('" "', 'NULL')
            
            data = dict(zip(header, re.split(' +', line)))
            sdate, stime = data['Date_Time'].split('_') 
            
            sensordate = map(int, sdate.split('.'))
            #sensordate = '%s/%s/20%s' % (sensordate[1].lstrip('0'), sensordate[0].lstrip('0'), sensordate[2])
            sensordate = '20%02i-%02i-%02i' % (sensordate[2], sensordate[1], sensordate[0])
            
            for c in channels:
                try:
                    sensortime, sensortemp = float(data['S%iM' % c]), float(data['S%iT' % c])
                except:                    
                    # print 'problem:', 'S%iT' % c, 'S%iM' % c #, data['S%iT' % c], data['S%iM' % c]
                    continue
                if not re.match('1[0-4]', stime):
                    continue
                if sensortime > 550.0 or sensortemp > 30.0:
                    print 'INSANITY', sensortime, sensortemp
                    continue
                temp_data[c][sensordate] = temp_data[c].get(sensordate, []) + [sensortemp]
                time_data[c][sensordate] = time_data[c].get(sensordate, []) + [sensortime] 
            pass
        
        dates = {}
        
        for c in sorted(channels):
            fig = plt.figure()
            fig.suptitle("Channel %i (%s) - STime vs Date" % (c, CHANNEL_SUBSTRATES[c]))
            ax = fig.add_subplot(111)
            ax.set_xlabel("Date")
            ax.set_ylabel("STime")
            x, y = [], []
            
            for sd in sorted(temp_data[c]):
                
                y.extend(time_data[c][sd])
                if not sd in dates:
                    # dates[sd] = len(dates) + 1
                    dates[sd] = 0
                #x.extend([dates[sd]] * len(time_data[c][sd]))
                x.extend([sd] * len(time_data[c][sd]))
                
                temp_data[c][sd] = median(temp_data[c][sd])
                time_data[c][sd] = median(time_data[c][sd])
                
                
            #print x
            for i, sd in enumerate(sorted(dates)):
                dates[sd] = i + 1
                print sd, dates[sd]
    
            x = map(lambda x:dates[x], x)
            
            ax.plot(x, y, 'b*')
            labels = [item.get_text() for item in ax.get_xticklabels()]
            print labels
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels(sorted(dates))
            #plt.xticks(np.arange(0, len(xlabels)), xlabels)
            plt.setp(plt.xticks()[1], rotation=90)
    
            plt.subplots_adjust(bottom=0.14)
    
            fig.savefig("channel_%i_stime_vs_date.png" % c)        
        
    return time_data
        
        
def plot_data(data):
    #fig = plt.figure()
    #fig.suptitle("Sensor Calibration")
    #ax = plt.subplot(1,1,1)
    pot_colors = {1: 'r', 2: 'g', 3: 'b', 4: 'y', 5: 'c', 6: 'm'}
    
    x_sand, y_sand = [], []
    x_peat, y_peat = [], []
    
    fig_sand = plt.figure()
    fig_sand.suptitle("Sensor Calibration - Sand")
    fig_peat = plt.figure()
    fig_peat.suptitle("Sensor Calibration - Peat")
    
    
    
    ax_sand = fig_sand.add_subplot(111)
    ax_peat = fig_peat.add_subplot(111)
    
    ax_sand.set_xlabel('RWC')
    ax_sand.set_ylabel('Sensor reading')
    ax_peat.set_xlabel('RWC')
    ax_peat.set_ylabel('Sensor reading')
    
    
    print sorted(data, key=lambda x:x[1])
    for key in sorted(data, key=lambda x:x[1]):
        if key[1] <= 3:
            x_sand.extend(data[key]['x'])
            y_sand.extend(data[key]['y'])
            ax_sand.plot(data[key]['x'], data[key]['y'], '%c%c' % (pot_colors[key[1]],
                                                                   CHANNEL_SYMBOLS[key[0]]))
        else:
            x_peat.extend(data[key]['x'])
            y_peat.extend(data[key]['y'])
            ax_peat.plot(data[key]['x'], data[key]['y'], '%c%c' % (pot_colors[key[1]],
                                                                   CHANNEL_SYMBOLS[key[0]]))
    
    z_sand = np.polyfit(x_sand, y_sand, 3)
    p_sand = np.poly1d(z_sand)
    xx = np.linspace(min(x_sand), 1, 100)
    ax_sand.plot(xx, p_sand(xx), '-k', linewidth=0.75)
    
    z_peat = np.polyfit(x_peat, y_peat, 3)
    p_peat = np.poly1d(z_peat)
    xx = np.linspace(min(x_peat), 1, 100)
    ax_peat.plot(xx, p_peat(xx), '-k', linewidth=0.75)
    
    fig_sand.savefig("sand_calibration.png")
    fig_peat.savefig("peat_calibration.png")
    """
    pot_colors = {1: 'r', 2: 'g', 3: 'b', 4: 'y', 5: 'c', 6: 'm'}
    
    c = 0
    fig = None
    for key in sorted(data, key=lambda x:x[1]):
        # if key[1] != 1: continue
        if c == 0:
            figname = 'Pot_%i_calibration.png' % key[1]            
            fig = plt.figure() 
            fig.suptitle("Sensor Calibration - Pot %i" % key[1])
            ax = plt.subplot(1,1,1)
        c += 1
        
        z4 = np.polyfit(data[key]['x'], data[key]['y'], 3)
        p4 = np.poly1d(z4)        
        
        ax.plot(data[key]['x'], data[key]['y'], '%c%c' % (pot_colors[key[1]],
                                                          CHANNEL_SYMBOLS[key[0]]))
        xx = np.linspace(0, 1, 100)
        ax.plot(xx, p4(xx), '-%c' % (pot_colors[key[1]]), linewidth=0.75)
        
        
        if c == 3:
            c = 0
            plt.savefig(figname)
    """                                  
            
    
    # plt.show()
    
    #ax.plot(range(len(xlabels)), row, style, label=str(i), linewidth=lwidth)
    pass
    

def process_data(Y_sensor, X_rwc):
    data = {}
    for channel in Y_sensor:
        pot = MAP_CHANNEL_POT[channel]
        for sdate in Y_sensor[channel]:
            y = Y_sensor[channel][sdate]
            try:
                x = X_rwc[pot - 1][sdate]
            except:
                continue
            if x is None or y is None:
                continue
            print channel, pot, sdate, x, y
            key = (channel, pot)
            if key not in data:
                data[key] =  {'x': [], 'y': []}
            data[key]['x'].append(x)
            data[key]['y'].append(y)
        
    return data



def main(argv):
    
    Y_sensor = read_sensor_data(argv[1], MAP_CHANNEL_POT.keys())
    X_rwc = read_potdata(argv[0])
    processed = process_data(Y_sensor, X_rwc)
    
    plot_data(processed)
    #print X_rwc
    #read_sensor_data(argv[1], [12])
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
