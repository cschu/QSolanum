#!/usr/bin/python

import os
import sys
import math
import glob

import sql
import process_xls as p_xls

DEFAULT_EXPERIMENT_ID = 1

""" Change to whatever is needed. """
DEFAULT_DATE_STR = ''

DB_NAME = 'trost_prod'
TABLE_NAME = 'cultures'
TABLE = [
    'id INT AUTO_INCREMENT',
    'name VARCHAR(45)', 
    'limsstudyid INT',
    'condition VARCHAR(45)',
    'created DATETIME',
    'description TEXT',
    'experiment_id INT',
    'plantspparcelle INT',
    'location_id INT',
    'planted DATE',
    'terminated DATE',
    'PRIMARY KEY(id)']

columns_d = {
    'Name': (0, 'name', str),
    'Study_Id': (1, 'limsstudyid', int),
    'condition': (2, 'condition', str),
    'created': (3, 'created', str),    
    'Description': (4, 'description', str),
    'experiment_id': (5, 'experiment_id', int),
    'Itempobject': (6, 'plantspparcelle', int),
    'location_id': (7, 'location_id', int),
    'planted': (8, 'planted', str),
    'terminated': (9, 'terminated', str)}


###
def main(argv):
    
    if len(argv) == 0:
        sys.stderr.write('Missing input file.\nUsage: python create_subspeciestable.py <dir>\n')
        sys.exit(1)
    
    sql.write_sql_header(DB_NAME, TABLE_NAME, TABLE)
    dir_name = argv[0]
    fn = '%s/%s' % (dir_name, 'culture_data.xls')
    data, headers  = p_xls.read_xls_data(fn)
    # return None
    for dobj in data:
        dobj.experiment_id = DEFAULT_EXPERIMENT_ID
        dobj.condition = ''
        dobj.created = DEFAULT_DATE_STR
    sql.write_sql_table(data, columns_d, table_name=TABLE_NAME)   

    return None

if __name__ == '__main__': main(sys.argv[1:])
