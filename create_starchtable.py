#!/usr/bin/python

import os
import sys
import math
import glob
# import _mysql

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
               
USE_DB = 'USE %s;'
DROP_TABLE = 'DROP TABLE %s;'
CREATE_TABLE = 'CREATE TABLE %s(\n%s\n);' 

def write_sql_header(out=sys.stdout):
    out.write('%s\n' % USE_DB % DB_NAME)
    out.write('%s\n' % DROP_TABLE % YIELD_TABLE_NAME)
    out.write('%s\n' % (CREATE_TABLE % (YIELD_TABLE_NAME, 
                                        ',\n'.join(YIELD_TABLE))))
    pass

INSERT_STR = 'INSERT INTO %s VALUES %s;\n'

columns_d = {'Name': (0, 'name', str), 
             'Aliquot_Id': (1, 'aliquot_id', int), 
             'Parzellennr': (2, 'parzellennr', int), 
             'Standort': (3, 'location_id', int),
             'Sorte': (4, 'cultivar', str),
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

def write_sql_table(data, table_name='DUMMY', out=sys.stdout, index=0):
    for dobj in data:
        entry = []        
        for key, val in columns_d.items():
            if hasattr(dobj, key) and getattr(dobj, key) != '':
                entry.append(val + (getattr(dobj, key),))
            else:
                entry.append(val[:-1] + (str, 'NULL'))
        entry = [(-1, 'id', int, index)] + entry
        index += 1
        try:
            out.write(INSERT_STR % (table_name,
                                    tuple([x[2](x[3]) 
                                           for x in sorted(entry)])))
        except:
            sys.stderr.write('EXC: %s\n' % sorted(entry))
            sys.exit(1)
        
    return index
                             
    



###
def main(argv):
    
    write_sql_header()
    # return None
    index = 0
    sheet_index=p_xls.DEFAULT_PARCELLE_INDEX 
    for fn in glob.glob('TROST_Knollenernte*.xls'):
        # print fn
        data, headers  = p_xls.read_xls_data(fn, sheet_index=sheet_index)       
        index = write_sql_table(data, table_name=YIELD_TABLE_NAME, index=index)
        print index


    return None

if __name__ == '__main__': main(sys.argv[1:])
