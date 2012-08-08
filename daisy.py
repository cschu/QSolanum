#!/usr/bin/python

import os
import sys
import math

import login
the_db = login.get_db()

import data_objects as DO
import compile_data as CD1
import compile_data2 as CD2
import queries
import write_table as WT

daisy_query = """
SELECT
starch_yield.name,
starch_yield.id as yield_id, 
staerkegehalt_g_kg, 
knollenmasse_kgfw_parzelle, 
cultures.plantspparcelle, 
locations.limsid as location_id, 
cultures.id as culture_id, 
cultures.name as culture_name, 
cultures.plantspparcelle,
cultures.planted,
cultures.terminated,
subspecies.cultivar as cultivar,
subspecies.id as sub_id,
subspecies.limsid as sub_limsid,
subspecies.breeder,
subspecies.reifegruppe,
treatments.id as treatment_id, 
value_id as treatment, 
starch_yield.aliquotid as plant_aliquot
FROM starch_yield, locations, cultures, treatments, subspecies
WHERE locations.id = starch_yield.location_id
AND treatments.aliquotid = starch_yield.aliquotid
AND cultures.location_id = starch_yield.location_id
AND subspecies.id != 37
AND subspecies.cultivar = starch_yield.cultivar
""".strip()


###
def main(argv):

    heat_d, h2o_d = CD2.get_climate_data()
    the_db.query(daisy_query)
    data = the_db.store_result().fetch_row(how=1, maxrows=0)
    data = [DO.StarchData(d.keys(), d.values()) for d in data]
    field_data = [d for d in data if d.location_id in CD2.FIELD_TRIALS]
    # print field_data
    field_results = CD1.compute_starch_rel_field(field_data,
                                                 CD2.FIELD_TRIALS, CD1.DROUGHT_ID)
    compiled = {}
    compiled.update(field_results)
    
    for k, v in sorted(compiled.items()):
        if isinstance(k, str): continue
        compiled[k].heat_sum, compiled[k].heat_nmeasures = heat_d[k[0]]
        compiled[k].limsloc = k[0]
        compiled[k].precipitation, compiled[k].prec_nmeasures = h2o_d[k[0]]

    WT.write_table(compiled, WT.FIELDS)
    return None

if __name__ == '__main__': main(sys.argv[1:])
