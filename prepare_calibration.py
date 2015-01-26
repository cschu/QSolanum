#!/usr/bin/env python
'''
Created on Oct 14, 2013

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import re
import csv
import datetime



import matplotlib.pyplot as plt


import numpy as np

SENSOR_SOURCE = {'44443': ['logger2_2011_05_19-2012_01_18.calibration.txt'],
                 '48656': ['logger1_2011_04_12-2012_12_06.calibration.txt',
                           'logger2_2011_05_19-2012_01_18.calibration.txt'],
                 '51790': ['logger2_2011_05_19-2012_01_18.calibration.txt',
                           'logger2_2012_01_26-2012_06_18.calibration.txt'],
                 '56575': ['logger2_2012_01_26-2012_06_18.calibration.txt'],
                 '56726': ['logger1_2011_04_12-2012_12_06.calibration.txt'],
                 '58243': ['logger2_2012_07_02-2013_02_09.calibration.txt'],
                 '60319': ['logger1_2012_12_06-2013_05_07.calibration.txt',
                           'logger2_2012_07_02-2013_02_09.calibration.txt'],
                 '62030': ['logger1_2012_12_06-2013_05_07.calibration.txt'],
                 '62326': ['logger1_2013_05_17-2013_08_14.calibration.txt']} 
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
                            datetime.datetime.strptime('2013-08-14', '%Y-%m-%d'))
                  }



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
        
        insane = 0
        total = 0
        
        for line in fi:
            
            line = line.strip().replace('" "', 'NULL')
            
            data = dict(zip(header, re.split(' +', line)))
            sdate, stime = data['Date_Time'].split('_') 
            
            sensordate = map(int, sdate.split('.'))
            #sensordate = '%s/%s/20%s' % (sensordate[1].lstrip('0'), sensordate[0].lstrip('0'), sensordate[2])
            sensordate = '20%02i-%02i-%02i' % (sensordate[2], sensordate[1], sensordate[0])
            
            for c in channels:
                total += 1
                try:
                    sensortime, sensortemp = float(data['S%iM' % c]), float(data['S%iT' % c])
                except:                    
                    # print 'problem:', 'S%iT' % c, 'S%iM' % c #, data['S%iT' % c], data['S%iM' % c]
                    continue
                if not re.match('1[0-4]', stime):
                    continue
                if sensortime > 550.0 or sensortemp > 30.0:
                    print 'INSANITY', sensortime, sensortemp
                    insane += 1
                    continue
                temp_data[c][sensordate] = temp_data[c].get(sensordate, []) + [sensortemp]
                time_data[c][sensordate] = time_data[c].get(sensordate, []) + [sensortime] 
            pass
        
    print total, insane
        
            
        
    return time_data



def read_logger_info(fn):
    data = []
    reader = csv.reader(open(fn, 'rb'), delimiter=',', quotechar='"')
    header = reader.next()
    for row in reader:
        row = row
        data.append(dict(zip(header, row)))
    return data

def prepare_data(channels, time_data, x=None, y=None, labels=None, dates=None, final_set=False, label='blue'):
    if dates is None:
        dates = {}
    if x is None:
        x = []
    if y is None:
        y = []
    if labels is None:
        labels = []
    
    for c in channels:
        for sd in sorted(time_data[c]):
            y.extend(time_data[c][sd])
            if not sd in dates:
                dates[sd] = 0
            x.extend([sd] * len(time_data[c][sd]))
            labels.extend([label] * len(time_data[c][sd]))
    
    if final_set:
        for i, sd in enumerate(sorted(dates)):
            dates[sd] = i + 1
            print sd, dates[sd]
        x = map(lambda x:dates[x], x)
    return x, y, labels, dates


def plot_data(x, y, labels, dates, experimentID, treatment, write_image=True):
    
    fig = plt.figure()
    fig.suptitle("Experiment: %s - %s" % (experimentID, treatment))
    ax = fig.add_subplot(111)
    ax.set_xlabel("Date")
    ax.set_ylabel("Sensor Time [s]")
    
    #plt.rc('xtick', labelsize=6)
    plt.setp(plt.xticks()[1], rotation=90, fontsize=6)
    plt.subplots_adjust(bottom=0.14)
    
    Y_bp = {k: dict() for k in labels}            
    
    for xyz in zip(x, y, labels):
        Y_bp[xyz[2]][xyz[0]] = Y_bp[xyz[2]].get(xyz[0], []) + [xyz[1]]
    
    for i, k in enumerate(Y_bp):
        bp = ax.boxplot([item[1] for item in sorted(Y_bp[k].items())])
        plt.setp(bp['boxes'], color=k)
        plt.setp(bp['caps'], color=k)
        plt.setp(bp['whiskers'], color=k)
        plt.setp(bp['fliers'], color=k)
        plt.setp(bp['medians'], color=k)
        
    
    ax.set_xticks(range(len(dates)))
    
    xtlabels = map(lambda x: x[1] if x[0] % 7 == 6 else '',
                   [(i, d) for i, d in enumerate(sorted(dates))])
    ax.set_xticklabels(xtlabels)
    
    if write_image:
        fig.savefig("%s_%s_STime_vs_Date.png" % (experimentID, treatment))  
    pass #return fig, ax, dates
    
    
 

    
    
    




def main(argv):
    
    
    fname = argv[0]
    logger_info = read_logger_info(fname)
    experimentID = fname.replace('sensor_', '').replace('.csv', '')
    channels = [int(linfo['Kanal_ID']) for linfo in logger_info]
    time_data = {c: {} for c in channels}
    for fn in SENSOR_SOURCE[experimentID]:
        tdata = read_sensor_data(fn, channels)
        # print tdata
        # sys.exit()
        for c in tdata:
            for sd in tdata[c]:
                sd_dt = datetime.datetime.strptime(sd, '%Y-%m-%d') 
                if sd_dt >= SENSOR_PERIODS[experimentID][0] and sd_dt <= SENSOR_PERIODS[experimentID][1]:
                    if sd not in time_data[c]:
                        time_data[c][sd] = []
                    time_data[c][sd].extend(tdata[c][sd])
                    # time_data[c][sd].sort()
    
    # print tdata
    drought = [linfo for linfo in logger_info if linfo['Treatment'].strip() == 'drought']
    control = [linfo for linfo in logger_info if linfo['Treatment'].strip() == 'control']
    #print logger_info
    
    
    
    
    print 'Plotting drought...'
    channels = [int(linfo['Kanal_ID']) for linfo in drought]
    x, y, labels, dates = prepare_data(channels, time_data, final_set=True)
    x_both, y_both, labels_both, dates_both = prepare_data(channels, time_data, label='red')        
    plot_data(x, y, labels, dates, experimentID, 'drought')
    print 'Plotting control...'
    channels = [int(linfo['Kanal_ID']) for linfo in control]
    x, y, labels, dates = prepare_data(channels, time_data, final_set=True)
    x_both, y_both, labels_both, dates_both = prepare_data(channels, time_data, x=x_both, y=y_both, labels=labels_both, 
                                                           dates=dates_both, label='blue')
    plot_data(x, y, labels, dates, experimentID, 'control')
    print 'Plotting combined...'
    plot_data(x_both, y_both, labels_both, dates_both, experimentID, 'combined')
    #fig_both, ax_both, fnout_both = prepare_plot(experimentID, 'combined')
    #fig_both, ax_both, dates = plot_data([int(linfo['Kanal_ID']) for linfo in control], time_data, fig_both, ax_both)
    #fig_both, ax_both = plot_data([int(linfo['Kanal_ID']) for linfo in drought], time_data, 
    #                              fig_both, ax_both, fnout=fnout_both, dates=dates)
    
    # print logger_info
    
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
