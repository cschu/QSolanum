#!/usr/bin/env python
'''
Created on Nov 1, 2012

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import time
import re
"""
chr10   923     972     FCD17BMACXX:6:1106:9798:50937#CGCGGTGA/1        40      -       chr10   BGI     gene    867     7617    .       .       .       ID=PGSC0003DMG400014403;Name="Formin 5" 49
"""

['chr10   923     972     FCD17BMACXX:6:1106:9798:50937#CGCGGTGA/1        40      -       chr10   BGI     gene    867     7617    .       .       .       ', 
 'PGSC0003DMG400014403;Name="Formin 5" 49']

['chr10', '923', '972', 'FCD17BMACXX:6:1106:9798:50937#CGCGGTGA/1', '40', '-', 'chr10', 'BGI', 'gene', '867', '7617', '.', '.', '.']



def main(argv):
    
    hit_regions = {}
    gene_dic = {}
    
    hits = []
    out = sys.stdout
    err = sys.stderr
    fn = argv[0]
    
    out.write('#Reading... %s\n' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    out.flush()
    for line in open(fn):
        left, right = line.split('ID=')
        left = left.split()
        pos = (left[6],) + tuple(left[9:11])
        read = left[:6]
        
        right = 'ID=' + right
        try:
            id_ = re.search('ID=[A-Z0-9]+;', right).group().lstrip('ID=')[:-1]
        except:
            id_ = None
        try:
            name_ = re.search('Name=".*"', right).group().lstrip('Name=')
        except:
            name_ = None
        try:
            parent_ = re.search('Parent=[A-Z0-9]+', right).group().lstrip('Parent=')
        except:
            parent_ = None
        # right = ('ID=' + right).split()[0]
        # right = right.split(';')
        
        hits.append((pos, read, id_, name_, parent_))
        
    out.write('#Merging... %s\n' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))    
    out.flush()
    for pos, read, id_, name_, parent_ in hits:
        hit_regions[pos] = hit_regions.get(pos, [(id_, name_, parent_)]) + [read]
    
    out.write('#Sorting... %s\n' % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    out.flush()
    genes_with_reads = sorted([(p, len(v) - 1, v[0][0], v[0][1], v[0][2]) for p, v in hit_regions.items()], 
                              key=lambda x:x[1], reverse=True)

    for p, v, id_, name_, parent_ in genes_with_reads:
        out_string = '%s,%s,%s,%s,%s,%s,%s' % (p + (id_, name_, parent_, v))
        out.write(out_string + '\n') 
        
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
