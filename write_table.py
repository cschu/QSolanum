#!/usr/bin/python

import os
import sys
import math

FIELDS = {
    'Location': (0, 'limsloc'),
    'Cultivar': (1, 'cultivar'),
    'Starch_Yield_Plant_rel': (2, 'rel_starch'),
    'Plants_Parcelle': (3, 'plantspparcelle'),
    'Planting_Date': (4, 'planted'),
    'Weed_Reduction_Date': (5, 'terminated'),
    'Heat_Summation': (6, 'heat_sum'),
    '#Climate_Measurements': (7, 'heat_nmeasures'),
    'Reifegruppe': (8, 'reifegruppe'),
    'Breeder': (9, 'breeder')
    }


def write_table(data, headers, out=sys.stdout):
    head_row = [y[1] for y in sorted([x[::-1] for x in headers.items()])]
    out.write('%s\n' % (','.join(head_row)))
    for d in data:
        if isinstance(d, str): continue
        row = []
        for head in headers:
            row.append((headers[head][0], 
                        getattr(data[d], headers[head][1])))
        row = [x[1] for x in sorted(row)]
        out.write('%s\n' % (','.join(map(str, row))))
        pass
    pass
        
            
        
    

###
def main(argv):
    return None

if __name__ == '__main__': main(sys.argv[1:])
