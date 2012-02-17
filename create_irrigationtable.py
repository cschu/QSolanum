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
TABLE_NAME = 'irrigation'
TABLE = [
    'id INT AUTO_INCREMENT',
    '`date` DATE',
    'treatment_id INT',
    'location_id INT',
    '`value` FLOAT',
    'PRIMARY KEY(id)'
    ]


# need 4 times these columns as we are going to parse the same file 4 times: for each possible type of treatment.
# column name in xls: (order, column name in sql, cast function[, lookup function])
columns_d = {
    'Datum': (0, 'date', str),
    'treatment_id': (1, 'treatment_id', int),
    'StandortID': (2, 'location_id', int),
}

extra_column_names = [ 'Kontrolle', 'Trockenstress', '50_%_nFK', '30_%_nFK' ]

#columns_d = [
#     {
#        'Datum': (0, 'date', str),
#        'Standort_ID': (2, 'location_id', int),
#        'Kontrolle': (3, 'value', str, 'custom'),
#     },
#     {
#        'Datum': (0, 'date', str),
#        'Standort_ID': (2, 'location_id', int),
#        'Trockenstress': (3, 'value', str, 'custom'),
#     },
#     {
#        'Datum': (0, 'date', str),
#        'Standort_ID': (2, 'location_id', int),
#        '50_%_nFK': (3, 'value', str, 'custom'),
#    },
#    {
#        'Datum': (0, 'date', str),
#        'Standort_ID': (2, 'location_id', int),
#        '30_%_nFK': (3, 'value', str, 'custom'),
#    }
#]

def annotate_locations(data):
    locations = sql.get_locations()
    for dobj in data:
        dobj.Standort = locations[dobj.Standort]
    return data
    



###
def main(argv):
    
    if len(argv) == 0:
        sys.stderr.write('Missing input file.\nUsage: python create_irrigationtable.py <dir>\n')
        sys.exit(1)
    
    sql.write_sql_header(DB_NAME, TABLE_NAME, TABLE)
    for fn in argv:
        data, headers  = p_xls.read_xls_data(fn)

        # find the right treatment columns: intersect two dicts
        treatment_column_names = [item for item in headers if item in extra_column_names]

        for column in treatment_column_names:
            for dobj in data:
                dobj.treatment_id = sql.get_value_id(column.replace('_', ' '))
            columns_d_extra = columns_d.copy()
            columns_d_extra[ column ] = (3, 'value', float)
            sql.write_sql_table(data, columns_d_extra, table_name=TABLE_NAME)   

    return None

if __name__ == '__main__': main(sys.argv[1:])
