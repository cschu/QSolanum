#!/usr/bin/python

import os
import sys
import math

USE_DB = 'USE %s;'
DROP_TABLE = 'DROP TABLE IF EXISTS %s;'
CREATE_TABLE = 'CREATE TABLE %s(\n%s\n) ENGINE=InnoDB DEFAULT CHARSET=utf8;' 
INSERT_STR = 'INSERT INTO %s VALUES %s;\n'

def write_sql_header(db_name, table_name, table, out=sys.stdout):
    out.write('%s\n' % USE_DB % db_name)
    out.write('%s\n' % DROP_TABLE % table_name)
    out.write('%s\n' % (CREATE_TABLE % (table_name,
                                        ',\n'.join(table))))
    pass

def format_entry(entry):
    """ This is a really really ugly workaround... """
    formatted = []
    for x in entry:
        if isinstance(x, str) and x != 'NULL':
            formatted.append("'%s'" % x)
        else:
            formatted.append(x)
    return '(%s)' % ','.join(map(str, formatted))
    

def write_sql_table(data, columns_d, table_name='DUMMY', out=sys.stdout):
    for dobj in data:
        entry = []        
        for key, val in columns_d.items():
            if hasattr(dobj, key) and getattr(dobj, key) != '':
                entry.append(val + (getattr(dobj, key),))
            else:
                entry.append(val[:-1] + (str, 'NULL'))
            pass

        entry = [(-1, 'id', str, 'NULL')] + entry # add the id

        try:
            out.write(INSERT_STR % (table_name,
                                    format_entry([x[2](x[3]) 
                                                  for x in sorted(entry)])))
        except:
            sys.stderr.write('EXC: %s\n' % sorted(entry))
            sys.exit(1)
        
    return None


###
def main(argv):
    return None

if __name__ == '__main__': main(sys.argv[1:])
