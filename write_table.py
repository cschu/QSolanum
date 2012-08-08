#!/usr/bin/python

import os
import sys
import math

FIELDS = {
    'Location': (0, 'limsloc'),
    'Cultivar': (1, 'cultivar'),
    'Cultivar_ID': (1.1, 'sub_limsid'),
    'Starch_Yield_Plant_rel': (2, 'rel_starch'),
    'Plants_Parcelle': (3, 'plantspparcelle'),
    'Planting_Date': (4, 'planted'),
    'Weed_Reduction_Date': (5, 'terminated'),
    'Heat_Summation': (6, 'heat_sum'),
    '#Temp_Measurements': (7, 'heat_nmeasures'),
    'Precipitation': (7.1, 'precipitation'),
    '#Prec_Measurements': (7.2, 'prec_nmeasures'),
    'Reifegruppe': (8, 'reifegruppe'),
    'Treatment': (8.1, 'treatment'),
    'Breeder': (9, 'breeder'),
    'Elevation': (10, 'elevation'),
    'Longitude': (11, 'longitude_e'),
    'Latitude': (12, 'latitude_n'),
    'Tuber_Yield_Abs': (13, 'knollenmasse_kgfw_parzelle')
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
