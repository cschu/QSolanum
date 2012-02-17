#!/usr/bin/python

import os
import sys
import math
import glob

import sql
import process_xls as p_xls


DB_NAME = 'trost_prod'
TABLE_NAME = 'locations'
TABLE = [
    'id INT AUTO_INCREMENT',
    'limsid INT',
    'name VARCHAR(45)',
    'elevation FLOAT',
    'gridref_north FLOAT',
    'gridref_east FLOAT',
    'PRIMARY KEY(id)']
               
columns_d = {'limsid': (0, 'limsid', int),
             'name': (1, 'name', str),
             'elevation': (2, 'elevation', float),
             'gridref_north': (3, 'gridref_north', float),
             'gridref_east': (4, 'gridref_east', float)}
    
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
    fn = '%s/%s' % (dir_name, 'locations_with_geodata.xls')
    data, headers  = p_xls.read_xls_data(fn)
    sql.write_sql_table(data, columns_d, table_name=TABLE_NAME)   

    return None

if __name__ == '__main__': main(sys.argv[1:])
