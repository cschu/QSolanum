#!/usr/bin/python

import os
import sys
import math
import glob
# import _mysql

import process_xls as p_xls

DB_NAME = 'trost_prod'

TREATMENT_TABLE_NAME = 'treatment'
TREATMENT_TABLE = [
    'id INT',
    'name VARCHAR(45)',
    'aliquot_id INT NOT NULL',
    'alias VARCHAR(45)',
    'treatment VARCHAR(45) NOT NULL',
    'PRIMARY KEY(id)']
               
USE_DB = 'USE %s;'
DROP_TABLE = 'DROP TABLE %s;'
CREATE_TABLE = 'CREATE TABLE %s(\n%s\n);' 

def write_sql_header(out=sys.stdout):
    out.write('%s\n' % USE_DB % DB_NAME)
    out.write('%s\n' % DROP_TABLE % TREATMENT_TABLE_NAME)
    out.write('%s\n' % (CREATE_TABLE % (TREATMENT_TABLE_NAME, 
                                        ',\n'.join(TREATMENT_TABLE))))
    pass

INSERT_STR = 'INSERT INTO %s VALUES %s;\n'



columns_d = {'Name': (0, 'name', str), 
             'Aliquot_Id': (1, 'aliquot_id', int), 
             'Alias': (2, 'alias', str),
             'Treatment': (3, 'treatment', str)
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
    sheet_index=p_xls.DEFAULT_TREATMENT_ALIQUOT_INDEX
    fn = 'treatmentaliquot.xls'
    data, headers  = p_xls.read_xls_data(fn, sheet_index=sheet_index)       
    index = write_sql_table(data, table_name=TREATMENT_TABLE_NAME, index=index)
        # print index


    return None

if __name__ == '__main__': main(sys.argv[1:])
