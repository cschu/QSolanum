#!/usr/bin/python

import os
import sys
import math

import login
the_db = login.get_db()
import data_objects as DO

###
def do_something():
    return None 


"""
mysql> select location_id, count(datum) from temps where (invalid is null or invalid !=1) group by location_id;
+-------------+--------------+
| location_id | count(datum) |
+-------------+--------------+
|           1 |          149 |
|           2 |          135 |
|           3 |          176 |
|           5 |          166 |
|           6 |          184 |
|           7 |          183 |
|           8 |          138 |
|           9 |          170 |
|          10 |          155 |
|          11 |          136 |
+-------------+--------------+
10 rows in set (0.00 sec)

mysql> select location_id, count(distinct datum) from temps where (invalid is null or invalid !=1) group by location_id;
+-------------+-----------------------+
| location_id | count(distinct datum) |
+-------------+-----------------------+
|           1 |                   148 |
|           2 |                   135 |
|           3 |                   176 |
|           5 |                   165 |
|           6 |                   153 |
|           7 |                   183 |
|           8 |                   138 |
|           9 |                   168 |
|          10 |                   155 |
|          11 |                   136 |
+-------------+-----------------------+
10 rows in set (0.03 sec)
"""


###
def main(argv):

    query = """SELECT * from temps WHERE location_id=3 AND invalid != 1O RDER BY datum""".strip()
    the_db.query(query)
    data = the_db.store_result().fetch_row(how=1, maxrows=0)

    print ','.join(map(str, data[0].keys()))

    for d in data:
        # dobj = DO.DataObject(d.keys(), d.values())
        print ','.join(map(str, d.values()))

    return None

if __name__ == '__main__': main(sys.argv[1:])
