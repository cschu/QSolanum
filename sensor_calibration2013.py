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

from scipy.odr import odrpack as odr
from scipy.odr import models

def poly_lsq(X, Y, n, itmax=200):
    func = models.polynomial(n)
    mydata = odr.Data(X, Y)
    myodr = odr.ODR(mydata, func, maxit=itmax)
    myodr.set_job(fit_type=2)
    fit = myodr.run()
    
    if fit.stopreason[0] == 'Iteration limit reached':
        print 'poly_lsq: Iteration limit reached, result not reliable!'
    coeff = fit.beta[::-1]
    err = fit.sd_beta[::-1]
    
    return coeff, err



SENSOR_KEYS = {1: [(1, 1, 47), (1, 2, 18), (1, 3, 32), (1, 4, 21), (1, 5, 41), (1, 6, 54)],
               2: [(1, 7, 17), (1, 8, 9), (1, 9, 3), (1, 10, 40), (1, 11, 8), (1, 12, 16)],
               3: [(1, 13, 44), (1, 14, 6), (1, 15, 23), (1, 16, 2), (1, 17, 10), (1, 18, 14)],
               4: [(1, 19, 51), (1, 20, 45), (1, 21, 59), (1, 22, 32), (1, 23, 5)],
               5: [(1, 24, 11), (1, 25, 26), (1, 26, 35), (1, 27, 46), (1, 28, 29), (1, 29, 37)],
               6: [(1, 30, 48), (1, 31, 49), (1, 32, 19), (1, 33, 50), (1, 34, 43), (1, 35, 58)]}

MAP_CHANNEL_POT = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1,
                   7: 2, 8: 2, 9: 2, 10: 2, 11: 2, 12: 2,
                   13: 3, 14: 3, 15: 3, 16: 3, 17: 3, 18: 3,
                   19: 4, 20: 4, 21: 4, 22: 4, 23: 4, 
                   24: 5, 25: 5, 26: 5, 27: 5, 28: 5, 29: 5,
                   30: 6, 31: 6, 32: 6, 33: 6, 34: 6, 35: 6}

CHANNEL_SUBSTRATES = {1: 'Sand', 2: 'Sand', 3: 'Sand', 4: 'Sand', 5: 'Sand', 6: 'Sand',
                      7: 'Sand', 8: 'Sand', 9: 'Sand', 10: 'Sand', 11: 'Sand', 12: 'Sand',
                      13: 'Sand', 14: 'Sand', 15: 'Sand', 16: 'Sand', 17: 'Sand', 18: 'Sand',
                      19: 'Peat', 20: 'Peat', 21: 'Peat', 22: 'Peat', 23: 'Peat', 
                      24: 'Peat', 25: 'Peat', 26: 'Peat', 27: 'Peat', 28: 'Peat', 29: 'Peat',
                      30: 'Peat', 31: 'Peat', 32: 'Peat', 33: 'Peat', 34: 'Peat', 35: 'Peat'}

CHANNEL_SYMBOLS = {1: 'o', 2: 'v', 3: '*', 4: 'D', 5: 'h', 6: 's',
                   7: 'o', 8: 'v', 9: '*', 10: 'D', 11: 'h', 12: 's',
                   13: 'o', 14: 'v', 15: '*', 16: 'D', 17: 'h', 18: 's',
                   19: 'o', 20: 'v', 21: '*', 22: 'D', 23: 'h', 
                   24: 'o', 25: 'v', 26: '*', 27: 'D', 28: 'h', 29: 's',
                   30: 'o', 31: 'v', 32: '*', 33: 'D', 34: 'h', 35: 's'}

W_EMPTY_POT_SAND = 0.26866 #kg
W_EMPTY_POT_PEAT = 0.06208 #kg
DRY_FRACTION_PEAT = 0.5316
DRY_FRACTION_SAND = 1.0000

W_EMPTY_BOX = 0.85675
DRY_FRACTION_PEAT_BOX = 0.579926886
DRY_FRACTION_SAND_BOX = 0.9201970443

PROBLEMATIC_SENSORS = (2, 3, 4, 6, 9, 11, 19, 22, 23, 24, 25, 28, 29, 31, 32, 33, 34)


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
        
        if awc < 0:
                errmsg = (awc, w_after_watering, self.w_empty, self.w_drysubstrate, self.sensor_weight)
                sys.stderr.write('ALERT: Negative water content: wc=%f weight=%f empty-weight=%f dw-substrate=%f sensor-weight=%f\n') % errmsg
        
        rwc = awc / self.water_capacity
        return awc, rwc
    pass


class Box(Pot):
    def __init__(self, w_empty):
        Pot.__init__(self)
        self.w_empty = w_empty
        pass
    pass

class SandBox(Box):
    def __init__(self, w_empty, dry_fraction):
        Box.__init__(self, w_empty)
        self.dry_fraction = dry_fraction
        pass
    pass

class PeatBox(Box):
    def __init__(self, w_empty, dry_fraction):
        Box.__init__(self, w_empty)
        self.dry_fraction = dry_fraction# DRY_FRACTION_PEAT_BOX


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
    
    #pots = [SandPot(), SandPot(), SandPot(), PeatPot(), PeatPot(), PeatPot()]
    pots = [SandBox(0.817, 0.92), SandBox(0.855, 0.917), SandBox(0.804, 0.909), 
            PeatBox(0.866, 0.576), PeatBox(0.858, 0.583), PeatBox(0.816, 0.580)]
    
    reader = csv.reader(open(fn, 'rb'), delimiter='\t', quotechar='"')
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
                    # print 'INSANITY', sensortime, sensortemp
                    continue                
                temp_data[c][sensordate] = temp_data[c].get(sensordate, []) + [sensortemp]
                time_data[c][sensordate] = time_data[c].get(sensordate, []) + [sensortime] 
            pass
        
        # if temperature-vs-time plots are needed, comment this block out and uncomment the next one
        for c in sorted(channels):
            for sd in sorted(temp_data[c]):
                temp_data[c][sd] = median(temp_data[c][sd])
                time_data[c][sd] = median(time_data[c][sd])
                
        """
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
                
            for i, sd in enumerate(sorted(dates)):
                dates[sd] = i + 1
                
    
            x = map(lambda x:dates[x], x)
            
            ax.plot(x, y, 'b*')
            labels = [item.get_text() for item in ax.get_xticklabels()]
            
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels(sorted(dates))
            #plt.xticks(np.arange(0, len(xlabels)), xlabels)
            plt.setp(plt.xticks()[1], rotation=90)
    
            plt.subplots_adjust(bottom=0.14)
    
            fig.savefig("channel_%i_stime_vs_date.png" % c)
        """
    return time_data
        
        
def plot_data(data, pot_colors={1: 'r', 2: 'g', 3: 'b', 4: 'y', 5: 'c', 6: 'm'}):
    
    def fit_curve2(X, Y, plot_, n=3):
        X, Y = [list(item) for item in zip(*sorted(zip(X, Y)))]
        Z = np.polyfit(X, Y, n)
        print Z
        # P = np.poly1d(Z)
        #X_curve = np.linspace(min(X), 1, 100)
        Z = poly_lsq(X, Y, n)[0]
        print Z
        Y_new = np.polyval(Z, X)
        # plot_.plot(X_curve, P(X_curve), '-k', linewidth=0.75)
        plot_.plot(X, Y_new, '-k', linewidth=2)
        pass
    def fit_curve(X, Y, plot_, n=3):
        P = np.polynomial.Polynomial((2392.8, -13.396, 0.0372, -5e-5, 3e-8)[::-1])#, [0, 1], [0,1])
        #X_curve = np.linspace(min(X), 1, 100)
        plot_.plot(sorted(X), P(sorted(X)), '-k', linewidth=2)        
        pass
    
    x_sand, y_sand, x_peat, y_peat = [], [], [], []
    fig_sand, fig_peat = plt.figure(), plt.figure()
    ax_sand, ax_peat = fig_sand.add_subplot(111), fig_peat.add_subplot(111)
    fig_sand.suptitle("Sensor Calibration - Sand")    
    fig_peat.suptitle("Sensor Calibration - Peat")
    ax_sand.set_xlabel('RWC')
    ax_sand.set_ylabel('Sensor reading')
    ax_peat.set_xlabel('RWC')
    ax_peat.set_ylabel('Sensor reading')
    
    print 'DATA:', sorted(data, key=lambda x:x[1])
    for key in sorted(data, key=lambda x:x[1]):
        
        #for xy in 
        
        
        fig_channel = plt.figure()
        ax_channel = fig_channel.add_subplot(111)
        fig_channel.suptitle('Sensor Data - Channel %i' % key[0])
        ax_channel.plot(data[key]['x'], data[key]['y'], '%c%c' % (pot_colors[key[1]],
                                                                  CHANNEL_SYMBOLS[key[0]]))
        fit_curve(data[key]['x'], data[key]['y'], ax_channel)
        fig_channel.savefig("channel_%i_calibration.png" % key[0])
        
        if key[0] in PROBLEMATIC_SENSORS: #(2, 3, 4, 6, 11, 12, 19, 23, 25, 28, 29, 32):
            continue
        
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
    print 'SAND', x_sand, y_sand
    print 'PEAT', x_peat, y_peat
    
    fit_curve(x_sand, y_sand, ax_sand, n=4)
    fit_curve(x_peat, y_peat, ax_peat, n=3)    
    
    data_out = open('sand_calibration.dat', 'wb')
    for x, y in zip(x_sand, y_sand):
        data_out.write('%f\t%f\n' % (x, y))
    data_out.close()
    
    data_out = open('peat_calibration.dat', 'wb')
    for x, y in zip(x_peat, y_peat):
        data_out.write('%f\t%f\n' % (x, y))
    data_out.close()
    
    fig_sand.savefig("sand_calibration.png")
    fig_peat.savefig("peat_calibration.png")
    
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
            # print 'C>', channel, pot, sdate, x, y
            key = (channel, pot)
            if key not in data:
                data[key] =  {'x': [], 'y': []}
            data[key]['x'].append(x)
            data[key]['y'].append(y)
        
    return data



def main(argv):
    
    Y_sensor = read_sensor_data(argv[1], MAP_CHANNEL_POT.keys())
    X_rwc = read_potdata(argv[0])
    
    print Y_sensor
    print
    print
    print X_rwc
    #sys.exit()
    processed = process_data(Y_sensor, X_rwc)
    
    print processed
    
    
    plot_data(processed)
    #print X_rwc
    #read_sensor_data(argv[1], [12])
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
    