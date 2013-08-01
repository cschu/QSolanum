#!/usr/bin/env python
'''
Created on Nov 6, 2012

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import csv
import glob
import re

def main2(argv):
    MIN_HITS = int(argv[0])
    files = argv[1:]
    genes = set([])
    gene_d = {}
              
    pattern = re.compile('ID=PGSC000[0-9]DMG[0-9]{9}') 
    
    for i, fn in enumerate(files):
        sys.stdout.write(' '.join(['Reading', fn, '%f%%' % ((i+1)/float(len(files))*100), '\n']))
        sys.stdout.flush()
        for line in open(fn, 'rb'):            
            # print line,
            try: 
                gid = pattern.search(line).group()
            except:
                # print 'FAIL'
                continue
            # print 'OK'
            # genes.add(gid)
            gene_d[gid] = gene_d.get(gid, 0) + 1
        
        genes = genes.union(set([gid for gid in gene_d if gene_d[gid] >= MIN_HITS]))
        gene_d = {}
    
    for gid in sorted(list(genes)):
        print gid
    print len(genes)
    
    pass

def main(argv):
    
    MIN_HITS = int(argv[0])
    files = argv[1:]
    
    genes = set([])
    # transcript_count = 0
    transcripts = set([])
    
    for i, fn in enumerate(files):
        # print i, fn
        print 'Reading', fn, '%f%%' % ((i+1)/float(len(files))*100)
        reader = csv.reader(open(fn, 'rb'), delimiter=',', quotechar='"')
        for row in reader:
            if row[0].strip().startswith('#'): 
                continue
            # print row
            gid, count = row[3], int(row[6])
            if re.search('DMT', gid):
                transcripts.add(gid)
                continue
            if count >= MIN_HITS:
                genes.add(gid)
    for gid in sorted(list(genes)):
        print gid
    print len(genes)
    print len(transcripts)
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
