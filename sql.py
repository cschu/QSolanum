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

INSERT_PLANTS2_STR = """
INSERT INTO plants2 
(id, aliquot, name, subspecies_id, location_id, culture_id, sampleid,
description, created)
SELECT NULL, %s, %s, subspecies.id, locations.id, %s, %s, '', ''
FROM subspecies, locations
WHERE subspecies.limsid = %s AND locations.limsid = %s;
""".strip()

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
    # return '(%s)' % ','.join(map(str, formatted))
    return formatted

    

def prepare_sql_table(data, columns_d):
    rows = []
    for dobj in data:
        row = []
        for key, val in columns_d.items():
            if hasattr(dobj, key) and getattr(dobj, key) != '':
                row.append(val + (getattr(dobj, key),))
            else:
                row.append(val[:-1] + (str, 'NULL'))
                pass
        row = [(-1, 'id', str, 'NULL')] + row # add the id
        rows.append(sorted(row))
    return rows


def write_standard_sql_table(rows, table_name='DUMMY', out=sys.stdout):
    for row in rows:
        try:       
            formatted = format_entry([x[2](x[3]) for x in row])
            entry = '(%s)' % ','.join(map(str, formatted))
            out.write(INSERT_STR % (table_name, entry))
        except:
            sys.stderr.write('EXC: %s\n' % row)
            sys.exit(1)
    pass

# legacy support
def write_sql_table(data, columns_d, table_name='DUMMY', out=sys.stdout):
    write_standard_sql_table(prepare_sql_table(data, columns_d),
                             table_name=table_name, out=out)
    pass
    

###
def main(argv):
    return None

if __name__ == '__main__': main(sys.argv[1:])
