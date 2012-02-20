#!/usr/bin/python

import os
import sys
import math

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
plants.aliquot as plant_aliquot,
plants.subspecies_id as psub_id
FROM starch_yield, locations, cultures, treatments, plants, subspecies
WHERE locations.id = starch_yield.location_id
AND treatments.aliquotid = starch_yield.aliquotid
AND plants.aliquot = starch_yield.aliquotid
AND plants.subspecies_id = subspecies.id
AND cultures.id = plants.culture_id
AND subspecies.id != 37
""".strip()

climate_query = """
SELECT
tmin, 
tmax, 
precipitation, 
datum, 
locations.limsid, 
locations.id, 
cultures.planted, 
cultures.terminated 
FROM temps, locations, cultures
WHERE temps.location_id = locations.id 
AND cultures.location_id = locations.id
AND temps.datum BETWEEN cultures.planted AND cultures.terminated
""".strip()

def main(argv):
    return None

if __name__ == '__main__': main(sys.argv[1:])
