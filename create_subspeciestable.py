#!/usr/bin/python

import os
import sys
import math
import glob

import sql
import process_xls as p_xls

DEFAULT_POTATO_ID = 1

DB_NAME = 'trost_prod'
TABLE_NAME = 'subspecies'
TABLE = [
    'id INT AUTO_INCREMENT',
    'species_id INT',
    'limsid INT',
    'cultivar VARCHAR(45)',
    'breeder VARCHAR(45)',
    'reifegruppe VARCHAR(10)',
    'krautfl INT',
    'verwendung VARCHAR(10)',
    'PRIMARY KEY(id)']
               
columns_d = {'LIMS_Subspecies_id': (0, 'limsid', int),      
             'species': (1, 'species_id', int),
             'SORTE': (2, 'cultivar', str),
             'ZUECHTER': (3, 'breeder', str),
             'REIFEGRP': (4, 'reifegruppe', str),
             'KRAUTFL': (5, 'krautfl', int),
             'Verwendung': (6, 'verwendung', str)}

def annotate_locations(data):
    locations = sql.get_locations()
    for dobj in data:
        dobj.Standort = locations[dobj.Standort]
    return data
    


###
def main(argv):
    
    if len(argv) == 0:
        sys.stderr.write('Missing input file.\nUsage: python create_subspeciestable.py <dir>\n')
        sys.exit(1)
    
    sql.write_sql_header(DB_NAME, TABLE_NAME, TABLE)
    dir_name = argv[0]
    fn = '%s/%s' % (dir_name, 'TROSTSorten2012.xls')
    data, headers  = p_xls.read_xls_data(fn)
    for dobj in data:
        dobj.species = DEFAULT_POTATO_ID
    sql.write_sql_table(data, columns_d, table_name=TABLE_NAME)   

    return None

if __name__ == '__main__': main(sys.argv[1:])
