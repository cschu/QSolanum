#!/usr/bin/python

import os
import sys
import math
import glob

import sql
import process_xls as p_xls

DB_NAME = 'trost_prod'
YIELD_TABLE_NAME = 'starch_yield'
YIELD_TABLE = [
    'id INT',
    'name VARCHAR(45)',
    'aliquot_id INT NOT NULL',
    'parzellennr INT',
    'location_id INT NOT NULL',
    'cultivar VARCHAR(45)',
    'pflanzen_parzelle INT',
    'knollenmasse_kgfw_parzelle DOUBLE NOT NULL',
    'staerkegehalt_g_kg DOUBLE NOT NULL',
    'staerkeertrag_kg_parzelle DOUBLE NOT NULL',
    'PRIMARY KEY(id)']
               
columns_d = {'Name': (0, 'name', str), 
             'Aliquot_Id': (1, 'aliquot_id', int), 
             'Parzellennr': (2, 'parzellennr', int), 
             'Standort': (3, 'location_id', int),
             'Sorte': (4, 'cultivar', lambda x:str(x).upper()),
             'Pflanzen_Parzelle': (5, 'pflanzen_parzelle', int),
             'Knollenmasse_kgFW_Parzelle': (6, 'knollenmasse_kgfw_parzelle', 
                                            float),
             'Staerkegehalt_g_kg': (7, 'staerkegehalt_g_kg', float),
             'Staerkeertrag_kg_Parzelle': (8, 'staerkeertrag_kg_parzelle', 
                                           float)}
default_values = {
    'Name': 'NULL',
    'Aliquot_Id': 0,
    'Parzellennr': 0,
    'Standort': 0,
    'Sorte': 'NULL',
    'Pflanzen_Parzelle': 0,
    'Knollenmasse_kgFW_Parzelle': 0.0,
    'Staerkegehalt_g_kg': 0.0,
    'Staerkeertrag_kg_Parzelle': 0.0             
    }


###
def main(argv):
    
    sql.write_sql_header(DB_NAME, YIELD_TABLE_NAME, YIELD_TABLE)
    index = 0
    sheet_index=p_xls.DEFAULT_PARCELLE_INDEX 
    for fn in glob.glob('TROST_Knollenernte*.xls'):
        data, headers  = p_xls.read_xls_data(fn, sheet_index=sheet_index)       
        index = sql.write_sql_table(data, columns_d, table_name=YIELD_TABLE_NAME, index=index)
        

    return None

if __name__ == '__main__': main(sys.argv[1:])
