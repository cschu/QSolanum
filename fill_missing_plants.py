#!/usr/bin/python

import sys

import sql
import ora_sql

###
def main(argv):
    missing_plant_ids = sql.get_missing_plants(2) + sql.get_missing_plants(7)

    trost_subspecies = sql.get_subspecies() # subspecies: PK id
    trost_cultures   = sql.get_cultures() # cultures: PK id
    bad_plants = []

    for aliquot_id in missing_plant_ids:
        plant = ora_sql.get_plant_information(aliquot_id)

        if trost_subspecies.has_key(plant['subspecies_id']):
            print """
            INSERT INTO `plants` (id, name, aliquot, culture_id, subspecies_id, created)
            VALUES (NULL, NULL, %d, %d, %d, NOW());
            """.strip() % (plant['aliquot_id'], trost_cultures[ plant['culture_id'] ], trost_subspecies[ plant['subspecies_id'] ])
        else:
            bad_plants.append(aliquot_id)

    if len(bad_plants) > 0:
        print bad_plants

if __name__ == '__main__': main(sys.argv[1:])
