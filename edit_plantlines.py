#!/usr/bin/env python

import sys
import re

import login
DB = login.get_db()
C = DB.cursor()

def getLineAlias(lname):
    re_hits = re.search('St\.(?P<c1>E|A).+St\.(?P<c2>A|R).+\}\.(?P<lid>[0-9]{1,3})\.|/', lname)
    try:
        return re_hits.group('c1') + re_hits.group('c2') + re_hits.group('lid')
    except:
        return 'NULL'


def main(argv):

    C.execute('SELECT id, name FROM plantlines;')
    errors = open('edit_plantlines.errors.txt', 'wb')
    
    for row in C.fetchall():
        lalias = getLineAlias(row[1])
        print row, lalias
    
        if lalias != 'NULL':
            stmt = "UPDATE plantlines SET line_alias = '%s' WHERE id = %i;" % (lalias, row[0])
            try:
                C.execute(stmt)
            except:
                DB.rollback()
                errors.write(stmt + '\n')
                continue
            DB.commit()

    errors.close()
    pass





if __name__ == '__main__': main(sys.argv[1:])
