#!/usr/bin/python

import os
import sys
import math
import glob

import sql
import process_xls as p_xls

""" Change to whatever is needed. """
DEFAULT_DATE_STR = ''

DB_NAME = 'trost_prod'
TABLE_NAME = 'plants2'

TABLE = [
    'id INT(11) AUTO_INCREMENT',
    'aliquot INT(11)',
    'name VARCHAR(45)', 
    'subspecies_id INT(11)',
    'location_id INT(11)',
    'culture_id INT(11)',
    'sampleid INT(11)',
    'description TEXT',
    'created DATETIME',
    'PRIMARY KEY(id)']

columns_d = {
    'Aliquot_Id': (0, 'aliquot', int),
    'Name': (1, 'name', str),
    'Subspecies_Id': (2, 'subspecies_id', int),
    'Location_Id': (3, 'location_id', int),
    'Culture_Id': (4, 'culture_id', int),
    'Sample_Id': (5, 'sampleid', int),
    'Description': (6, 'description', str),
    'created': (7, 'created', str)}
    



###
def main(argv):
    
    if len(argv) == 0:
        sys.stderr.write('Missing input file.\nUsage: python create_plants2table.py <dir>\n')
        sys.exit(1)
    
    sql.write_sql_header(DB_NAME, TABLE_NAME, TABLE)
    dir_name = argv[0]
    fn = '%s/%s' % (dir_name, 'current_plants.xls')
    data, headers  = p_xls.read_xls_data(fn)

    """
    Some plants do not have a subspecies id - causing trouble
    further downstream. Hence, I
    inserted dummy into subspecies table:
    insert into subspecies values(NULL, -1, 1, 'UNKNOWN', NULL, NULL, 
    NULL, NULL);
    """
    for dobj in data:
        dobj.created = DEFAULT_DATE_STR
        if dobj.Subspecies_Id == '':
            dobj.Subspecies_Id = -1
            
    """ 
    Table writing logic is specific to this table,
    therefore it does not use sql.write_sql_table.
    """
    for row in sql.prepare_sql_table(data, columns_d):
        # print row
        try:
            """
            This adds the required values for subspecies.limsid 
            and locations.limsid to the insert query.
            TODO: culture-id!, possibly sample-id!
            """
            entry = [x[2](x[3])
                     for x in row[1:3] + row[5:7]]
            entry += (int(row[3][3]), int(row[4][3]))
            entry = tuple(entry)

            sys.stdout.write('%s\n' % (sql.INSERT_PLANTS2_STR % entry))
        except:
            sys.stderr.write('EXC: %s\n' % row)
            sys.exit(1)

    return None

if __name__ == '__main__': main(sys.argv[1:])
