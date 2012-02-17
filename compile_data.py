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
    median_all = median([dobj.starch_abs for dobj in data])
    for trial in trials:
        loc_data = [d for d in data if d.location_id == trial]
        by_cult = group_by(loc_data, 'sub_id')
        for cultivar, samples in by_cult.items():
            key = (trial, int(cultivar), drought_id)            
            rel_starch = median([dobj.starch_abs/median_all
                                 for dobj in samples])
            results[key] = DO.CompiledData()
            results[key].eat_starch_data(samples[0])
            results[key].rel_starch = rel_starch

            if len(samples) != 2:
                """ 
                Boehlendorf (4451) & Norika GL (4452) 
                should be solved.
                """
                print 'PROBLEM', trial, cultivar
    
    results['median_all'] = median_all
    return results

    



starch_query= """
SELECT starch_yield.id, staerkegehalt_g_kg, knollenmasse_kgfw_parzelle, pflanzen_parzelle, locations.limsid as location_id, cultivar, treatments.id, value_id as treatment
FROM treatments 
INNER JOIN (starch_yield 
INNER JOIN locations ON locations.id = starch_yield.location_id) 
ON treatments.aliquotid = starch_yield.aliquotid
""".strip()



climate_query = """
SELECT rainfall, tmin, tmax, locations.limsid, locations.id
FROM temps
LEFT JOIN (locations)
ON (locations.id = temps.location_id)
ORDER BY locations.limsid
""".strip()




###
# TODO: keep computation within plant life period!
def compute_heat_summation(data):
    """
    What happens when there are differences in the 
    number of temperature measurements for the individual
    locations? 
    """
    heat_d = {}
    for dobj in data:
        if dobj.heat_sum is None:
            continue
            
        # key = tuple(map(int, (dobj.limsid, dobj.id)))
        key = int(dobj.limsid)
        heat_d[key] = heat_d.get(key, []) + [dobj.heat_sum]
        
    for k in heat_d:
        # print k, heat_d[k]
        heat_d[k] = (sum(heat_d[k]), len(heat_d[k]))
    return heat_d


###
def main(argv):
    the_db.query(climate_query)
    data = the_db.store_result().fetch_row(how=1, maxrows=999999)

    data = [DO.ClimateData(d.keys(), d.values()) for d in data]
    
    print [str(x) for x in data]
    
    print 'lims_loc\tloc\theat_sum\t#temps\n'
    for k, v in compute_heat_summation(data).items():
        print '%i\t%i\t%.3f\t%i' % (k + v), v[0]/v[1]
    

###
def main_starch(argv):
    the_db.query(starch_query)
    data = the_db.store_result().fetch_row(how=1, maxrows=999999)
    
    data = [DO.StarchData(d.keys(), d.values()) for d in data]
    """ TODO: global plants/parcelle! """

    # print compute_starch_rel_controlled(data, 4537)    
    # print compute_starch_rel_dethlingen(data)
    
    print compute_field_trials(data)

    return None

if __name__ == '__main__': main_starch(sys.argv[1:])
