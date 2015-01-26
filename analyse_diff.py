#!/usr/bin/env python
'''
Created on Nov 5, 2012

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import csv

def main(argv):
    fn = argv[0]
    reader = csv.reader(open(fn, 'rb'), delimiter='\t', quotechar='"')
    for row in reader:
        if row[0] != 'test_id': 
            q1, q2 = map(int, [c[1] for c in row[4:6]])
            # if q2 > 4 and q2 != q1 + 4:
            #    continue
            if q1 == 1:
                if q2 == 2:
                    row.append('control')
                elif q2 == 3:
                    row.append('replicate')
                else:
                    continue
            elif q2 == 4:
                if q1 == 2:
                    row.append('replicate')
                elif q1 == 3:
                    row.append('stress')
                else:
                    continue
            else:
                continue
            
            # if q2 == q1 + 4:
            #     row.append('replicate')
            # elif q2 <= 4:
            #     row.append('control')
            # elif q1 > 4:
            #     row.append('stress')
            # else:
            #     continue
                
        sys.stdout.write('\t'.join(row) + '\n')
        pass 
        
    
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
