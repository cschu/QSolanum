#!/usr/bin/python

import os
import sys
import math
import glob

import sql
import process_xls as p_xls

""" Change to whatever is needed. """
DEFAULT_DATE_STR = ''

DB_NAME = 'trost_prod'
TABLE_NAME = 'plants2'

TABLE = [
    'id INT(11) AUTO_INCREMENT',
    'aliquot INT(11)',
    'name VARCHAR(45)', 
    'subspecies_id INT(11)',
    'location_id INT(11)',
    'culture_id INT(11)',
    'sampleid INT(11)',
    'description TEXT',
    'created DATETIME',
    'PRIMARY KEY(id)']

columns_d = {
    'Aliquot_Id': (0, 'aliquot', int),
    'Name': (1, 'name', str),
    'Sample_Id_-_Subspecies_Id': (2, 'subspecies_id', int),
    'Location_Id_-_Location_Id': (3, 'location_id', int),
    'Culture_-_Study_Id': (4, 'culture_id', int),
    'Sample_Id_-_Sample_Id': (5, 'sampleid', int),
    'Description': (6, 'description', str),
    'created': (7, 'created', str)}
    

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
    fn = '%s/%s' % (dir_name, 'culture_data.xls')
    data, headers  = p_xls.read_xls_data(fn)
    for dobj in data:
        dobj.created = DEFAULT_DATE_STR
    sql.write_sql_table(data, columns_d, table_name=TABLE_NAME)   

    return None

if __name__ == '__main__': main(sys.argv[1:])
