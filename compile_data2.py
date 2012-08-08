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

def get_climate_data():
    the_db.query(queries.climate_query)
    climate_data = the_db.store_result().fetch_row(how=1, maxrows=0)
    climate_data = [DO.ClimateData(d.keys(), d.values()) 
                    for d in climate_data]
    heat_d, h2o_d = CD1.compute_climate_data(climate_data)
    return heat_d, h2o_d

def get_irrigation_data():
    the_db.query(queries.irrigation_query)
    irri_data = the_db.store_result().fetch_row(how=1, maxrows=0)
    irri_data = [DO.DataObject(d.keys(), d.values()) for d in irri_data]
    irrigation_d = {}
    for dobj in irri_data:
        key = (dobj.limsid, dobj.treatment_id)
        irrigation_d[key] = irrigation_d.get(key, 0) + dobj.irrigation_amount
    return irrigation_d

def annotate_compiled_data(compiled, heat_d, h2o_d, irrigation_d):
    for k, v in sorted(compiled.items()):
        if isinstance(k, str): continue
        try:
            compiled[k].heat_sum, compiled[k].heat_nmeasures = heat_d[k[0]]
        except:
            compiled[k].heat_sum, compiled[k].heat_nmeasures = 0.0, -1
        try:
            compiled[k].precipitation, compiled[k].prec_nmeasures = h2o_d[k[0]]
        except:
            compiled[k].precipitation, compiled[k].prec_nmeasures = 0.0, -1
        compiled[k].limsloc = k[0]
        
        irr_key = (compiled[k].limsloc, compiled[k].treatment)
        compiled[k].precipitation += irrigation_d.get(irr_key, 0)
    return compiled


###
def main(argv):
    

    heat_d, h2o_d = get_climate_data()
    irrigation_d = get_irrigation_data()    

    the_db.query(queries.starch_query)    
    data = the_db.store_result().fetch_row(how=1, maxrows=0)

    data = [DO.StarchData(d.keys(), d.values()) for d in data]

    golm_data = CD1.group_by([d for d in data if d.location_id == 4537],
                             'sub_id')
    dethl_data = CD1.group_by([d for d in data if d.location_id == 5519],
                              'sub_id')
    field_data = [d for d in data if d.location_id in FIELD_TRIALS]

    jki_gh_data = CD1.group_by([d for d in data if d.location_id == 6019],
                               'sub_id')
    jki_sh_data = CD1.group_by([d for d in data if d.location_id == 6020],
                               'sub_id')
    

    jki_gh_results = CD1.compute_starch_rel_ctrl(jki_gh_data, 6019,
                                                 [CD1.DROUGHT_ID])
    jki_sh_results = CD1.compute_starch_rel_ctrl(jki_sh_data, 6020,
                                                 [CD1.DROUGHT_ID])

    golm_results = CD1.compute_starch_rel_ctrl(golm_data, 4537, 
                                               [CD1.DROUGHT_ID])
    dethl_results = CD1.compute_starch_rel_ctrl(dethl_data, 5519,
                                                CD1.DETHLINGEN_DROUGHT_IDS)
    field_results = CD1.compute_starch_rel_field(field_data,
                                                 FIELD_TRIALS, CD1.DROUGHT_ID)


    all_results = [(jki_gh_results, 'JKI_CGW'),
                   (jki_sh_results, 'JKI_SHE'),
                   (golm_results, 'MPI_FIELD'),
                   (dethl_results, 'DET_FIELD'),
                   (field_results, 'ALL_FIELD')]

    """
    compiled = {}
    # compiled.update(golm_results)
    compiled.update(dethl_results)
    # compiled.update(field_results)
    # compiled.update(jki_sh_results)
    # compiled.update(jki_gh_results)
    """
    
    for data, name in all_results:
        print name
        annotate_compiled_data(data, heat_d, h2o_d, irrigation_d)
        WT.write_table(data, WT.FIELDS, 
                       out=open('STARCH_REL_%s.csv' % name, 'w'))

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
