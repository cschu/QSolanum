#!/usr/bin/python

import os
import sys
import math

import _mysql

import login
the_db = login.get_db()

import process_xls as p_xls


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
    loc_data = [d for d in data if d.location_id == location]
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
    loc_data = [d for d in data if d.location_id == 5519]
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
                         if dobj.location_id in FIELD_TRIALS])
    for trial in FIELD_TRIALS:
        loc_data = [d for d in data if d.location_id == trial]
        by_cult = group_by_cultivar(loc_data)
        for cultivar, samples in by_cult.items():
            key = (cultivar, 'drought')
            results[key] = median([dobj.starch_abs
                                   for dobj in samples])
            print len([dobj.starch_abs
                       for dobj in samples])
            
    return results, median_all

    

starch_query = """
SELECT starch_yield.id, staerkegehalt_g_kg, knollenmasse_kgfw_parzelle, pflanzen_parzelle, location_id, cultivar, treatments.id, treatment 
FROM starch_yield 
LEFT JOIN (treatments) 
ON (starch_yield.aliquotid = treatments.aliquotid)
""".strip()

climate_query = """
SELECT rainfall, tmin, tmax, locations.limsid, locations.id
FROM temps
LEFT JOIN (locations)
ON (locations.id = temps.location_id)
ORDER BY locations.limsid
""".strip()

###
def calc_heat_sum(t_range, tbase=6.0):
    """
    Daily heat summation is defined as:
    heat_sum_d = max(tx - tbase, 0), with    
    tx = (tmin + tmax)/2 and
    tmax = min(tmax_measured, 30.0) 
    """
    tmax = min(t_range[1], 30.0)
    tx = (t_range[0] + tmax) / 2.0
    return max(tx - tbase, 0.0)


###
def compute_heat_summation(data):
    """
    What happens when there are differences in the 
    number of temperature measurements for the individual
    locations? 
    """
    heat_d = {}
    for dobj in data:
        if dobj.tmin is None or dobj.tmax is None: 
            print 'TROUBLE', dobj
            continue            
            
        key = tuple(map(int, (dobj.limsid, dobj.id)))
        heat_d[key] = heat_d.get(key, []) + [calc_heat_sum((dobj.tmin,
                                                            dobj.tmax))]
        
    for k in heat_d:
        # print k, heat_d[k]
        heat_d[k] = (sum(heat_d[k]), len(heat_d[k]))
    return heat_d


###
def main(argv):
    the_db.query(climate_query)
    data = the_db.store_result().fetch_row(how=1, maxrows=999999)

    data = [p_xls.DataObject(d.keys(), d.values()) for d in data]
    
    print [str(x) for x in data]
    
    print 'lims_loc\tloc\theat_sum\t#temps\n'
    for k, v in compute_heat_summation(data).items():
        print '%i\t%i\t%.3f\t%i' % (k + v), v[0]/v[1]
    

###
def main_starch(argv):
    the_db.query(starch_query)
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
