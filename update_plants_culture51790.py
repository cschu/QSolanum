#!/usr/bin/env python
'''
Created on Dec 6, 2012

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys

import login

UPDATE_QUERY = """
UPDATE plants
SET subspecies_id = %i, name = '%s', culture_id = 51790
WHERE id = %i;
""".strip().replace('\n', ' ')



def main(argv):
    
    db = login.get_db()
    C = db.cursor()
    
    for line in open(argv[0]):
        line = line.strip().split()
        if len(line) > 0:
            pid, name, subspecies = int(line[0]), line[2], int(line[4])
            query = UPDATE_QUERY % (subspecies, name.strip('"'), pid)
            print query
            # continue
            try:
                C.execute(query)
                db.commit()
            except:
                sys.stdout.write('QUERY FAILED: \n%s\n' % query)
                db.rollback()
                sys.exit(1)
                
        
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
