#!/usr/bin/python

import os
import sys
import math

USE_DB = 'USE %s;'
DROP_TABLE = 'DROP TABLE %s;'
CREATE_TABLE = 'CREATE TABLE %s(\n%s\n);' 
INSERT_STR = 'INSERT INTO %s VALUES %s;\n'

def write_sql_header(db_name, table_name, table, out=sys.stdout):
    out.write('%s\n' % USE_DB % db_name)
    out.write('%s\n' % DROP_TABLE % table_name)
    out.write('%s\n' % (CREATE_TABLE % (table_name,
                                        ',\n'.join(table))))
    pass

def write_sql_table(data, columns_d, table_name='DUMMY', out=sys.stdout, index=0):
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
    return None

if __name__ == '__main__': main(sys.argv[1:])
