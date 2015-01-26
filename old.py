#!/usr/bin/python

import os
import sys
import math

"""
Heat summation periods
Day of planting -> Day of weed reduction

Buetow (5546): no weed reduction, harvest date: Sep 22-23
Petersgroden (5543): multiple weed reduction on Sep 3, 8, 17
Schrobenhausen (5539): no weed reduction, harvest date: Sep 26

according to Karin (mail from Feb 1, 2012):
Buetow, Schrobenhausen: weed reduction date = harvest date - 14d
Petersgroden: Sep 3
"""
PLANT_LIFETIMES_2011 = {
    5544: ('2011-04-18', '2011-09-06'),
    5541: ('2011-03-31', '2011-08-14'),
    5546: ('2011-04-29', '2011-09-08'),
    5519: ('2011-03-31', '2011-08-14'),
    4537: ('2011-03-31', '2011-08-14'),  
    5540: ('2011-04-15', '2011-09-01'),
    5542: ('2011-04-12', '2011-09-27'),
    5543: ('2011-04-19', '2011-09-03'),
    5539: ('2011-04-11', '2011-09-12'),
    5545: ('2011-04-11', '2011-09-03')
    }

#
def compute_starch_rel_controlled(data, location, drought_id=DROUGHT_ID):
    results = {}
    for cultivar, samples in data.items():
        ctrl_yield = median([dobj.starch_abs
                             for dobj in samples
                             if is_control(dobj.treatment)])
        key = (location, cultivar, drought_id)
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



###
#
def compute_starch_rel_controlled2(data, location):
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

            
            

def write_sql_table_old(data, columns_d, table_name='DUMMY', out=sys.stdout):
    for dobj in data:
        entry = []        
        for key, val in columns_d.items():
            if hasattr(dobj, key) and getattr(dobj, key) != '':
                entry.append(val + (getattr(dobj, key),))
            else:
                entry.append(val[:-1] + (str, 'NULL'))
            pass

        entry = [(-1, 'id', str, 'NULL')] + entry # add the id

        try:
            out.write(INSERT_STR % (table_name,
                                    format_entry([x[2](x[3]) 
                                                  for x in sorted(entry)])))
        except:
            sys.stderr.write('EXC: %s\n' % sorted(entry))
            sys.exit(1)
        
    return None




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

starch_query_old = """
SELECT starch_yield.id, staerkegehalt_g_kg, knollenmasse_kgfw_parzelle, pflanzen_parzelle, location_id, cultivar, treatments.id, value_id as treatment
FROM starch_yield 
LEFT JOIN (treatments) 
ON (starch_yield.aliquotid = treatments.aliquotid)
""".strip()

starch_query_try = """
SELECT starch_yield.id, staerkegehalt_g_kg, knollenmasse_kgfw_parzelle, pflanzen_parzelle, location_id, cultivar, treatments.id, value_id as treatment
FROM treatments
LEFT OUTER JOIN 
(starch_yield INNER JOIN locations ON locations.id = starch_yield.location_id)
ON treatments.aliquotid = starch_yield.aliquotid WHERE starch_yield.id
""".strip()


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
def main(argv):
    return None

if __name__ == '__main__': main(sys.argv[1:])
