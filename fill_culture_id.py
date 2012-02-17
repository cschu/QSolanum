#!/usr/bin/python

import os
import sys

import sql
import ora_sql
import data_objects 

###
def main(argv):
    trost_plants = sql.get_plants()
    trost_cultures = sql.get_cultures()

    bad_plants = []

    for aliquot_id, plant_id in trost_plants.iteritems():
        culture_id = ora_sql.get_culture_id(aliquot_id)
        if (trost_cultures.has_key(culture_id)):
            print "UPDATE `plants` SET culture_id = %d WHERE id = %d;" % (trost_cultures[culture_id], plant_id)
        else:
            bad_plants.append(plant_id)

    if len(bad_plants) > 0:
        print bad_plants

    return None

if __name__ == '__main__': main(sys.argv[1:])
