#!/usr/bin/python

import os
import sys
import math
import csv


import login
the_db = login.get_db()

###
def main(argv):

    first_line = True
    for line in csv.reader(open(argv[0], 'rb')):
        if first_line:
            first_line = False
        else:
            aliquot = int(line[0])
            the_db.query('SELECT * FROM aliquots WHERE aliquot=%i;' % \
                             aliquot)
            data = the_db.store_result().fetch_row(how=0, maxrows=0)            
            if len(data) > 0: print data
            pass

    return None

if __name__ == '__main__': main(sys.argv[1:])
