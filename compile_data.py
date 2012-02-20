#!/usr/bin/python

import os
import sys
import math

import _mysql

import login
the_db = login.get_db()

import data_objects as DO

CONTROLLED_TRIALS = [4537, 5506]
FIELD_TRIALS = [5544, 5541, 5546, 5540, 5542, 5543, 5539, 5545]
DETHLINGEN_TRIALS = [5519]

DROUGHT_ID = 170
DETHLINGEN_DROUGHT_IDS = (170, 172)
CONTROL_IDS = (169, 171)




#
def group_by_cultivar(data):
    grouped = {}
    for dobj in data:
        key = dobj.cultivar.upper()
        grouped[key] = grouped.get(key, []) + [dobj]
    return grouped

#
def group_by(data, field):
    grouped = {}
    for dobj in data:
        try:
            key = getattr(dobj, field)
        except:
            sys.stderr.write('Group by: Missing field!\n')
            sys.exit(1)
        # key = dobj.sub_id
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
def is_control(treatment):
    return treatment in CONTROL_IDS

#
def compute_starch_rel_ctrl(data, location, drought_ids):
    results = {}
    for cultivar, samples in data.items():
        ctrl_yield = median([dobj.starch_abs
                             for dobj in samples
                             if is_control(dobj.treatment)])
        for trmt in drought_ids:
            key = (location, int(cultivar), trmt)
            rel_starch = median([dobj.starch_abs/ctrl_yield
                                 for dobj in samples
                                 if dobj.treatment == trmt])
            results[key] = DO.CompiledData()
            results[key].eat_starch_data(samples[0])
            results[key].rel_starch = rel_starch
    return results

#
def compute_starch_rel_field(data, trials, drought_id):
    results = {}    
    # median_all = median([dobj.starch_abs for dobj in data])

    by_cult = group_by(data, 'sub_id')
    median_yields = dict([(k, median([dobj.starch_abs for dobj in by_cult[k]]))
                          for k in by_cult])
    # print median_yields
    # sys.exit(1)
    for trial in trials:
        loc_data = [d for d in data if d.location_id == trial]
        by_cult = group_by(loc_data, 'sub_id')
        for cultivar, samples in by_cult.items():
            key = (trial, int(cultivar), drought_id)            
            """
            rel_starch = median([dobj.starch_abs/median_yields[cultivar]
                                 for dobj in samples])
            """
            rel_starch = median([dobj.starch_abs for dobj in samples])
            rel_starch /= median_yields[cultivar]

            results[key] = DO.CompiledData()
            results[key].eat_starch_data(samples[0])
            results[key].rel_starch = rel_starch

            if len(samples) != 2:
                """ 
                Boehlendorf (4451) & Norika GL (4452) 
                should be solved.
                """
                print 'PROBLEM', trial, cultivar
    
    # results['median_all'] = median_all
    return results

###
def compute_climate_data(data):
    """
    Heat summation and sum of precipitation/irrigation.
    What happens when there are differences in the 
    number of temperature measurements for the individual
    locations? 
    """
    heat_d = {}
    h2o_d = {}
    for dobj in data:
        # key = tuple(map(int, (dobj.limsid, dobj.id)))
        key = int(dobj.limsid)
        if dobj.heat_sum is None:
            pass
        else:            
            heat_d[key] = heat_d.get(key, []) + [dobj.heat_sum]
        if dobj.precipitation is None:
            pass
        else:
            h2o_d[key] = h2o_d.get(key, []) + [dobj.precipitation]
        
    for k in heat_d:
        # print k, heat_d[k]
        heat_d[k] = (sum(heat_d[k]), len(heat_d[k]))
    for k in h2o_d:
        h2o_d[k] = (sum(h2o_d[k]), len(h2o_d[k]))
    return heat_d, h2o_d


###
def main(argv):
    """
    the_db.query(climate_query)
    data = the_db.store_result().fetch_row(how=1, maxrows=999999)

    data = [DO.ClimateData(d.keys(), d.values()) for d in data]
    
    print [str(x) for x in data]
    
    print 'lims_loc\tloc\theat_sum\t#temps\n'
    for k, v in compute_heat_summation(data).items():
        print '%i\t%i\t%.3f\t%i' % (k + v), v[0]/v[1]
    """
    return None

###
def main_starch(argv):
    """
    the_db.query(starch_query)
    data = the_db.store_result().fetch_row(how=1, maxrows=999999)
    
    data = [DO.StarchData(d.keys(), d.values()) for d in data]
    # print compute_starch_rel_controlled(data, 4537)    
    # print compute_starch_rel_dethlingen(data)
    
    print compute_field_trials(data)
    """
    return None

if __name__ == '__main__': main_starch(sys.argv[1:])
