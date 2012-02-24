#!/usr/bin/python

import os
import sys
import math

golm_starch_query = """
SELECT 
samples.name as sample_name,
plants.id as plant_id,
`values`.attribute as v_attr,
phenotype_values.number as x_weight,
cultures.plantspparcelle, 
locations.limsid as location_id, 
locations.elevation,
locations.gridref_north as latitude_n,
locations.gridref_east as longitude_e,
cultures.id as culture_id, 
cultures.name as culture_name, 
cultures.plantspparcelle,
cultures.planted,
cultures.terminated,
subspecies.cultivar as cultivar,
subspecies.id as sub_id,
subspecies.limsid as sub_limsid,
subspecies.breeder,
subspecies.reifegrclass as reifegruppe,
treatments.id as treatment_id, 
treatments.value_id as treatment, 
plants.aliquot as plant_aliquot,
plants.subspecies_id as psub_id
FROM starch_yield, locations, cultures, treatments, plants, subspecies, 
samples, phenotypes, `values`, phenotype_values
WHERE samples.plant_id = plants.id 
AND phenotypes.sample_id = samples.id
AND phenotype_values.phenotype_id = phenotypes.id
AND `values`.id = phenotype_values.value_id
AND `values`.id = 69
AND locations.id = cultures.location_id
AND treatments.aliquotid = starch_yield.aliquotid
AND plants.aliquot = starch_yield.aliquotid
AND plants.subspecies_id = subspecies.id
AND cultures.id = plants.culture_id
AND subspecies.id != 37
""".strip()

starch_query = """
SELECT
starch_yield.name,
starch_yield.id as yield_id, 
staerkegehalt_g_kg, 
knollenmasse_kgfw_parzelle, 
cultures.plantspparcelle, 
locations.limsid as location_id, 
locations.elevation,
locations.gridref_north as latitude_n,
locations.gridref_east as longitude_e,
cultures.id as culture_id, 
cultures.name as culture_name, 
cultures.plantspparcelle,
cultures.planted,
cultures.terminated,
subspecies.cultivar as cultivar,
subspecies.id as sub_id,
subspecies.limsid as sub_limsid,
subspecies.breeder,
subspecies.reifegrclass as reifegruppe,
treatments.id as treatment_id, 
treatments.value_id as treatment, 
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
AND (invalid != 1 OR invalid is NULL)
""".strip()

def main(argv):
    return None

if __name__ == '__main__': main(sys.argv[1:])
