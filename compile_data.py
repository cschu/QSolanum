#!/usr/bin/python

import os
import sys
import math

import _mysql

import login
the_db = _mysql.connect(host=login.DB_HOST,
                        user=login.DB_USER,
                        passwd=login.DB_PASS,
                        db=login.DB_NAME)
import process_xls as p_xls


"""
|  1 |   5544 | Atting                 |
|  2 |   5541 | Boehlendorf            |
|  3 |   5546 | Buetow                 |
|  4 |   5506 | JKI Grossluesewitz      |
|  5 |   5540 | Kaltenberg             |
|  6 |   5519 | LWK Dethlingen         |
|  7 |   5542 | Norika Gross Luesewitz |
|  8 |   5543 | Petersgroden           |
|  9 |   5539 | Schrobenhausen         |
| 10 |   5545 | Windeby                |
| 11 |   4537 | Golm                   |
"""
CONTROLLED_TRIALS = [4537, 5506]
FIELD_TRIALS = [5544, 5541, 5546, 5540, 5542, 5543, 5539, 5545]
DETHLINGEN_TRIALS = [5519]

#
def calc_starch_abs(starch_content, yield_tuber, nplants):
    if nplants is None:
        nplants = 16
    return (starch_content * yield_tuber) / float(nplants)    

#
def compute_starch_abs(data):
    for d in data: 
        d.starch_abs = calc_starch_abs(d.staerkegehalt_g_kg,
                                       d.knollenmasse_kgfw_parzelle,
                                       d.pflanzen_parzelle)
        print d.__dict__


    return data

#
def group_by_cultivar(data):
    grouped = {}
    for dobj in data:
        key = dobj.cultivar.upper()
        grouped[key] = grouped.get(key, []) + [dobj]
    return grouped

#
def median(v):
    # print v
    v_sorted = sorted(v)
    n = len(v)
    if n % 2 == 0:
        return (v_sorted[n/2-1] + v_sorted[n/2])/2.0
    else:
        return v_sorted[n/2]
#

#
def compute_starch_rel_controlled(data, location):
    """ GOLM/JKI """
    results = {}
    loc_data = [d for d in data if d.locationid == location]
    by_cult = group_by_cultivar(loc_data)
    for cultivar, samples in by_cult.items():
        ctrl_yield = median([dobj.starch_abs 
                             for dobj in samples
                             if dobj.treatment == 'control'])
        key = (cultivar, 'drought')
        results[key] = median([dobj.starch_abs/ctrl_yield
                               for dobj in samples
                               if dobj.treatment == 'drought'])       
        return results

#
def compute_starch_rel_dethlingen(data):
    """ Dethlingen """
    
    results = {}
    loc_data = [d for d in data if d.locationid == 5519]
    by_cult = group_by_cultivar(loc_data)
    for cultivar, samples in by_cult.items():
        ctrl_yield = median([dobj.starch_abs 
                             for dobj in samples
                             if dobj.treatment == '50 % nFK'])
        for trmt in ['drought', '30 % nFK']:
            key = (cultivar, trmt)
            results[key] = median([dobj.starch_abs/ctrl_yield
                                   for dobj in samples
                                   if dobj.treatment == trmt])       
    return results



#
def compute_field_trials(data):
    results = {}
    
    median_all = median([dobj.starch_abs for dobj in data                      
                         if dobj.locationid in FIELD_TRIALS])
    for trial in FIELD_TRIALS:
        loc_data = [d for d in data if d.locationid == trial]
        by_cult = group_by_cultivar(loc_data)
        for cultivar, samples in by_cult.items():
            key = (cultivar, 'drought')
            results[key] = median([dobj.starch_abs
                                   for dobj in samples])
            print len([dobj.starch_abs
                       for dobj in samples])
            
    return results, median_all

    

the_query = """
SELECT starch_yield.id, staerkegehalt_g_kg, knollenmasse_kgfw_parzelle, pflanzen_parzelle, locationid, cultivar, treatments.id, treatment 
FROM starch_yield 
LEFT JOIN (treatments) 
ON (starch_yield.aliquotid = treatments.aliquotid)
"""

###
def main(argv):
    the_db.query(the_query.strip())
    data = the_db.store_result().fetch_row(how=1, maxrows=999999)
    
    data = [p_xls.DataObject(d.keys(), d.values()) for d in data]
    """ TODO: global plants/parcelle! """

    data = compute_starch_abs(data)
    print 'xxx', data[0].__dict__

    # print compute_starch_rel_controlled(data, 4537)
    
    # print compute_starch_rel_dethlingen(data)
    
    print compute_field_trials(data)

    return None

if __name__ == '__main__': main(sys.argv[1:])
