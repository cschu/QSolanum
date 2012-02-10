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

"""
Heat summation periods
Day of planting -> Day of weed reduction

Buetow (5546): no weed reduction, harvest date: Sep 22-23
Petersgroden (5543): multiple weed reduction on Sep 3, 8, 17
Schrobenhausen (5539): no weed reduction, harvest date: Sep 26
"""
PLANT_LIFETIMES_2011 = {
    5544: ('2011-04-18', '2011-09-06'),
    5541: ('2011-03-31', '2011-08-14'),
    5546: ('2011-04-29', '2011-09-22'),
    5519: ('2011-03-31', '2011-08-14'),
    4537: ('2011-03-31', '2011-08-14'),  
    5540: ('2011-04-15', '2011-09-01'),
    5542: ('2011-04-12', '2011-09-27'),
    5543: ('2011-04-19', '2011-09-03'),
    5539: ('2011-04-11', '2011-09-26'),
    5545: ('2011-04-11', '2011-09-03')
    }



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

def is_control(treatment):
    return treatment in [169, 171]

DROUGHT_ID = 170
DETHLINGEN_DROUGHT_IDS = (170, 172)
#
def compute_starch_rel_controlled(data, location):
    """ GOLM/JKI """
    results = {}
    loc_data = [d for d in data if d.location_id == location]
    by_cult = group_by_cultivar(loc_data)
    for cultivar, samples in by_cult.items():
        ctrl_yield = median([dobj.starch_abs 
                             for dobj in samples
                             if is_control(dobj.treatment)])
        key = (location, cultivar, DROUGHT_ID)
        results[key] = median([dobj.starch_abs/ctrl_yield
                               for dobj in samples
                               if not is_control(dobj.treatment)])       
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
                             if is_control(dobj.treatment)])
        for trmt in DETHLINGEN_DROUGHT_IDS:
            key = (5519, cultivar, trmt)
            results[key] = median([dobj.starch_abs/ctrl_yield
                                   for dobj in samples
                                   if dobj.treatment == trmt])       
    return results



#
def compute_field_trials(data):
    results = {}    

    print set([dobj.location_id for dobj in data])

    median_all = median([dobj.starch_abs for dobj in data                      
                         if dobj.location_id in FIELD_TRIALS])
    for trial in FIELD_TRIALS:
        loc_data = [d for d in data if d.location_id == trial]
        by_cult = group_by_cultivar(loc_data)
        for cultivar, samples in by_cult.items():
            key = (trial, cultivar, DROUGHT_ID)            
            results[key] = median([dobj.starch_abs
                                   for dobj in samples])
            if len(samples) != 2:
                """ Boehlendorf (4451) & Norika GL (4452) """
                print 'PROBLEM', trial, cultivar
            
    return results, median_all

    



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
            
        key = tuple(map(int, (dobj.limsid, dobj.id)))
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
