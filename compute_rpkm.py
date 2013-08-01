#!/usr/bin/env python
'''
Created on Nov 2, 2012

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import re
import time
import os

total_mult_reads = {'1': 2039214,
                    '2': 2028311,
                    '3': 1950752,
                    '4': 1941006,
                    '5': 2049139,
                    '6': 2078695,
                    '7': 2064709,
                    '8': 2185939,
                    '9': 1850641,
                    '10': 2020929,
                    '11': 1850447,
                    '12': 1797046,
                    '13': 1852632,
                    '14': 1859688,
                    '15': 1935688,
                    '16': 1845867,
                    '17': 1919325,
                    '18': 1936966,
                    '19': 2097413,
                    '20': 1728466,
                    '21': 1669416,
                    '22': 1955665,
                    '23': 1902278,
                    '24': 1804551,
                    '25': 1812835,
                    '26': 2099713,
                    '27': 2063595,
                    '28': 1916892,
                    '29': 1886618,
                    '30': 2043797,
                    '31': 1983784,
                    '32': 1966078}


total_uniq_reads = {'1': 8028135,
                    '2': 7578996,
                    '3': 7642513,
                    '4': 8054488,
                    '5': 7889001,
                    '6': 7869979,
                    '7': 7722923,
                    '8': 8446059,
                    '9': 8227501,
                    '10': 7960477,
                    '11': 7610366,
                    '12': 8052966,
                    '13': 8254420,
                    '14': 8119736,
                    '15': 8069001,
                    '16': 8439008,
                    '17': 8439344,
                    '18': 8355227,
                    '19': 8410127,
                    '20': 8054615,
                    '21': 7915927,
                    '22': 8148816,
                    '23': 8447425,
                    '24': 8345386,
                    '25': 7984850,
                    '26': 8356702,
                    '27': 8295887,
                    '28': 8247646,
                    '29': 8293937,
                    '30': 8015534,
                    '31': 8509081,
                    '32': 8468648}


all_mapped_reads = dict([(k, total_uniq_reads[k] + total_mult_reads[k]) 
                         for k in total_uniq_reads])

total_reads = {'1': 11933625,
               '2': 11505686,
               '3': 11253755,               
               '4': 11793559,
               '5': 11610871,
               '6': 11659289,
               '7': 11568562,
               '8': 12387862,
               '9': 12062887,
               '10': 11695980,
               '11': 11094405,
               '12': 11798489,               
               '13': 12257682,
               '14': 11944563,
               '15': 11705361,
               '16': 12342816,
               '17': 12255400,
               '18': 12285214,               
               '19': 12470075,
               '20': 11669434,
               '21': 11625726,               
               '22': 11784131,
               '23': 12462653,
               '24': 12170236,
               '25': 11812052,
               '26': 12199070,
               '27': 12282323,
               '28': 11982641,
               '29': 12067964,
               '30': 11742997,
               '31': 12353727,
               '32': 12216392}

def compute_rpkm(sample_id, transcript_id, n_exon_reads, exon_dict, all_reads=total_uniq_reads):
    N = all_reads[sample_id]
    C = n_exon_reads
    L = int(exon_dict[transcript_id])#/1000.
    # return 10.0**9 * C / (N * L)
    return 10**9 * float(C) / (N * L)



def main(argv):

    transcripts = {}
    
    fn = argv[0]
    out = sys.stdout
    err = sys.stderr
    
    sample_id = os.path.basename(fn).split('_')[0]
    
    exon_dict = dict([tuple(line.strip().split(',')) 
                      for line in open('transcript_sizes.csv').readlines()])
     
    
    err.write('#Reading... %s\n' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    for line in open(fn):
        try:
            parents = re.search('Parent=([A-Z0-9]+,?)+', line).group().replace('Parent=', '').strip().split(',')
        except:
            parents = []
        for pid in parents:
            transcripts[pid] = transcripts.get(pid, 0) + 1
        pass
    
    err.write('#Sorting... %s\n' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    for k, v in sorted(transcripts.items(), key=lambda x:x[1], reverse=True):
        try:
            rpkm = compute_rpkm(sample_id, k, v, exon_dict, all_reads=all_mapped_reads)
        except:
            rpkm = -1.0
        out.write('%s,%i,%.5f\n' % (k, v, rpkm))
        pass
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
