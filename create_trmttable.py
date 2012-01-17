#!/usr/bin/python

import os
import sys
import math
import glob

import process_xls as p_xls
import sql

DB_NAME = 'trost_prod'
TREATMENT_TABLE_NAME = 'treatment'
TREATMENT_TABLE = [
    'id INT',
    'name VARCHAR(45)',
    'aliquot_id INT NOT NULL',
    'alias VARCHAR(45)',
    'treatment VARCHAR(45) NOT NULL',
    'PRIMARY KEY(id)']

columns_d = {'Name': (0, 'name', str), 
             'Aliquot_Id': (1, 'aliquot_id', int), 
             'Alias': (2, 'alias', str),
             'Treatment': (3, 'treatment', str)
             }
    
###
def main(argv):
    
    if len(argv) == 0:
        sys.stderr.write('Missing input file.\nUsage: python create_trmttable.py <filename>\n')
        sys.exit(1)

    sql.write_sql_header(DB_NAME, TREATMENT_TABLE_NAME, TREATMENT_TABLE)
    index = 0
    sheet_index=p_xls.DEFAULT_TREATMENT_ALIQUOT_INDEX

    fn = argv[0]
    data, headers  = p_xls.read_xls_data(fn, sheet_index=sheet_index)       
    index = sql.write_sql_table(data, columns_d, 
                                table_name=TREATMENT_TABLE_NAME, index=index)
    return None

if __name__ == '__main__': main(sys.argv[1:])
