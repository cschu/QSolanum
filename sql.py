#!/usr/bin/python

import os
import sys
import math

import login
the_db = login.get_db()

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



""" SQL Queries """

location_query = """
SELECT id, limsid FROM locations
""".strip()

value_query = """
select `values`.id, content, value from `values`
join i18n on foreign_key = values.id
where locale = 'en_us'
and `model` = 'value'
and attribute = 'Behandlung'
and field = 'value'
""".strip()

cultures_q = """
SELECT limsstudyid, id FROM cultures
""".strip()

plant_ids_q = """
SELECT aliquot, id FROM plants
""".strip()

subspecies_q = """
SELECT limsid, id FROM subspecies
""".strip()

missing_plants_q = """
select aliquotid from starch_yield where aliquotid not in (select 
aliquotid from starch_yield, plants where location_id=%s AND 
aliquotid=plants.aliquot order by cultivar) AND location_id=%s;
""".strip()

get_value_id_q = """
SELECT id FROM `values` WHERE value=%s;
""".strip()

def get_missing_plants(location_id):
    q    = the_db.query(missing_plants_q % (location_id, location_id))
    data = the_db.store_result().fetch_row(how=0, maxrows=0)
    rs   = [d[0] for d in data]
    return rs

def _get_table(query, key_key, pk_key='id'):
    query = the_db.query(query)
    data = the_db.store_result().fetch_row(how=1, maxrows=0)
    #print data
    rs = dict() 
    for d in data:
        cast_key_key = 'None'
        # lame casting solution
        if type(d[key_key]) is str: cast_key_key = int(d[key_key])
        rs[cast_key_key] = int(d[pk_key])
    return rs

def get_subspecies():
    return _get_table(subspecies_q, 'limsid')

def get_cultures():
    return _get_table(cultures_q, 'limsstudyid')

def get_plants():
    return _get_table(plant_ids_q, 'aliquot')

def get_locations():
    return _get_table(location_query, 'limsid')

def get_values():
    query = the_db.query(value_query)
    data = the_db.store_result().fetch_row(how=1, maxrows=200)
    id_of = dict()
    for d in data:
        id_of[str(d['content'])] = int(d['id'])
        id_of[str(d['value'])]   = int(d['id'])
    id_of[''] = '0' # add the empty value
    return id_of

def get_value_id(value):
    c = the_db.cursor()
    c.execute(get_value_id_q, (value,))
    data = c.fetchall()
    if len(data) > 0:
        if len(data[0]) > 0:
            return data[0][0]
    return None


""" Output """

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
#                if len(val) == 4: # ok, it has a lookup function for the value, so use it
#                    if val[3] == 'custom':
#                        val = val[:3]
#                    else:
#                        print locals()[ val[3] ]( getattr(dobj, key) )
#                        val = val[:3] + locals()[ val[3] ]( getattr(dobj, key) )
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
  
def write_update_sql(): pass
  

###
def main(argv):
    return None

if __name__ == '__main__': main(sys.argv[1:])
