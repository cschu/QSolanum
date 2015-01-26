#!/usr/bin/env python
'''
Created on Nov 6, 2012

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import re
import os

from collections import defaultdict

def count_genes_in_file(fn):        
    gene_d = {}
    pattern = re.compile('ID=PGSC000[0-9]DMG[0-9]{9}') 
    
    for line in open(fn, 'rb'):
        try:
            gid = pattern.search(line).group().lstrip('ID=')
        except:
            continue
        gene_d[gid] = gene_d.get(gid, 0) + 1
    return gene_d
    

def main(argv):
    
    gene_d = defaultdict(dict)
    file_ids = []
    out = sys.stdout
    
    for fn in argv:
        counts = count_genes_in_file(fn)
        fid = int(os.path.basename(fn).split('_')[0])
        file_ids.append(fid)
        for gid, count in counts.items():
            gene_d[gid][fid] = count
             
        pass
    
    file_ids = sorted(file_ids)
    out.write('\t'.join(['GeneID'] + map(str, file_ids) + ['\n']))
    for gid, counts in gene_d.items():
        string = '\t'.join([gid] + [str(counts.get(fid, '')) for fid in file_ids])
        out.write('%s\n' % string)
        out.flush()    
                
    pass

if __name__ == '__main__': main(sys.argv[1:])
