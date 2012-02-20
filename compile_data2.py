#!/usr/bin/python

import os
import sys
import math

import login
the_db = login.get_db()

import data_objects as DO
import compile_data as CD1
import queries

import write_table as WT

CONTROLLED_TRIALS = [4537, 5506]
FIELD_TRIALS = [5544, 5541, 5546, 5540, 5542, 5543, 5539, 5545]
DETHLINGEN_TRIALS = [5519]

def write_table_f(data, out=sys.stdout):
    by_loc = {}
    for k, v in data.items():
        by_loc[k[0]] = by_loc.get(k[0], []) + [k[1:] + (v,)]
    # print 5541, sorted(by_loc[5541])
    # print 5542, sorted(by_loc[5542])
    # return None
    for k, rows in sorted(by_loc.items()):
        for row in rows:
            out.write('%i,%s,%i,%.5f\n' % ((k,) + row))
    pass


###
def main(argv):
    
    """ 
    Climate data
    """
    
    the_db.query(queries.climate_query)
    climate_data = the_db.store_result().fetch_row(how=1, maxrows=0)
    climate_data = [DO.ClimateData(d.keys(), d.values()) 
                    for d in climate_data]
    heat_d, h2o_d = CD1.compute_climate_data(climate_data)
    # print heat_d
    

    
    # return None
    the_db.query(queries.starch_query)
    data = the_db.store_result().fetch_row(how=1, maxrows=9999999)

    data = [DO.StarchData(d.keys(), d.values()) for d in data]

    golm_data = CD1.group_by([d for d in data if d.location_id == 4537],
                             'sub_id')
    dethl_data = CD1.group_by([d for d in data if d.location_id == 5519],
                              'sub_id')
    field_data = [d for d in data if d.location_id in FIELD_TRIALS]
    
    golm_results = CD1.compute_starch_rel_ctrl(golm_data, 4537, 
                                               [CD1.DROUGHT_ID])
    dethl_results = CD1.compute_starch_rel_ctrl(dethl_data, 5519,
                                                CD1.DETHLINGEN_DROUGHT_IDS)
    field_results = CD1.compute_starch_rel_field(field_data,
                                                 FIELD_TRIALS, CD1.DROUGHT_ID)
    # print field_results


    compiled = {}
    # compiled.update(golm_results)
    # compiled.update(dethl_results)
    compiled.update(field_results)
    for k, v in sorted(compiled.items()):
        if isinstance(k, str): continue
        # print k
        compiled[k].heat_sum, compiled[k].heat_nmeasures = heat_d[k[0]]
        compiled[k].limsloc = k[0]
        compiled[k].precipitation, compiled[k].prec_nmeasures = h2o_d[k[0]]
        # print v
    # print heat_d
    
    WT.write_table(compiled, WT.FIELDS)

    return None
    
    """
    results = CD1.compute_starch_rel_controlled(data, 4537)
    write_table(results)
    # return None
    
    
    results = CD1.compute_starch_rel_dethlingen(data)
    write_table(results)
    # return None
    """


    # results = CD1.compute_field_trials(data)
    # write_table(results[0])
    # return None
    
if __name__ == '__main__': main(sys.argv[1:])
