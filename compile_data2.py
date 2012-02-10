#!/usr/bin/python

import os
import sys
import math

import login
the_db = login.get_db()

import data_objects as DO

import compile_data as CD1

CONTROLLED_TRIALS = [4537, 5506]
FIELD_TRIALS = [5544, 5541, 5546, 5540, 5542, 5543, 5539, 5545]
DETHLINGEN_TRIALS = [5519]

starch_query = """
SELECT
starch_yield.name,
starch_yield.id as yield_id, 
staerkegehalt_g_kg, 
knollenmasse_kgfw_parzelle, 
cultures.plantspparcelle, 
locations.limsid as location_id, 
cultures.id as culture_id, 
cultures.name as culture_name, 
subspecies.cultivar as cultivar,
subspecies.id as sub_id,
treatments.id as treatment_id, 
value_id as treatment, 
plants.aliquot as plant_aliquot,
plants.subspecies_id as psub_id
FROM starch_yield, locations, cultures, treatments, plants, subspecies
WHERE locations.id = starch_yield.location_id
AND treatments.aliquotid = starch_yield.aliquotid
AND plants.aliquot = starch_yield.aliquotid
AND plants.subspecies_id = subspecies.id
AND cultures.id = plants.culture_id
""".strip()

def write_table(data, out=sys.stdout):
    by_loc = {}
    for k, v in data.items():
        by_loc[k[0]] = by_loc.get(k[0], []) + [k[1:] + (v,)]
    print by_loc

    for k, rows in sorted(by_loc.items()):
        for row in rows:
            out.write('%i,%s,%i,%.5f\n' % ((k,) + row))
    pass


###
def main(argv):
    the_db.query(starch_query)
    data = the_db.store_result().fetch_row(how=1, maxrows=9999999)

    data = [DO.StarchData(d.keys(), d.values()) for d in data]
    for d in data:
        if int(d.location_id) == 4537:
            print d.__dict__


    """
    results = CD1.compute_starch_rel_controlled(data, 4537)
    write_table(results)
    return None

    results = CD1.compute_starch_rel_dethlingen(data)
    write_table(results)
    return None
    """

    results = CD1.compute_field_trials(data)
    write_table(results[0])
    return None

if __name__ == '__main__': main(sys.argv[1:])
