#!/usr/bin/env python
'''
Created on Dec 10, 2012

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import login
import csv

TREATMENT_QUERY = """
SELECT v.value 
FROM phenotype_plants pp, phenotypes p, `values` v 
WHERE pp.plant_id=%i AND
p.entity_id=805 AND 
p.id=pp.phenotype_id AND
v.id=p.value_id;
""".strip().replace('\n', ' ')

translate = {'Kontrolle': 'control', 
             'Trockenstress': 'drought'}


def main(argv):
    db = login.get_db()
    C = db.cursor()
    
    reader = csv.reader(open(argv[0], 'rb'), delimiter=',', quotechar='"')
    for row in reader:
        row = [cell for cell in row if len(cell) > 0]
        tmt = row[-1].strip()        
        for pid in map(int, row[:-1]):
            q = TREATMENT_QUERY % pid
            C.execute(q)
            tmt_indb = None
            for r in C.fetchall():
                tmt_indb = r[0]
                break
            if tmt_indb is None:
                print 'Problem: %i has no associated treatment.' % pid
            elif translate[tmt_indb].strip() != tmt:
                print 'Problem: %i is associated with a different treatment (%s) than expected' % (tmt_indb, pid)
            else:
                print '%i is OK' % pid                
                pass
    
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
