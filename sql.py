#!/usr/bin/python

import os
import sys
import math

import login
the_db = login.get_db()

location_query = """
SELECT id, limsid FROM locations
""".strip()

def get_locations():
    query = the_db.query(location_query)
    data = the_db.store_result().fetch_row(how=1, maxrows=99)
    # print data
    return dict([(int(d['limsid']), int(d['id'])) for d in data])

USE_DB = 'USE %s;'
DROP_TABLE = 'DROP TABLE IF EXISTS %s;'
CREATE_TABLE = 'CREATE TABLE %s(\n%s\n) ENGINE=InnoDB DEFAULT CHARSET=utf8;' 
INSERT_STR = 'INSERT INTO %s VALUES %s;\n'
"""
INSERT_SELECT_STR = ''
insert into plants (id, location_id) select NULL, locations.id from locations where locations.limsid = 1111;
"""

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
