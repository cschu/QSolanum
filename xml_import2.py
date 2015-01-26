#!/usr/bin/env python
'''
Created on Jul 30, 2013

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys

import login

import OpenPyXl as opx
from PhenoImporter import PhenoImporter 

def main(argv):
    
    TROST_DB = login.get_db(db='trost_prod')
    errorlog = open(argv[0].rstrip('.xlsx') + '.sql_errors.txt', 'w')
    sqlfile = open(argv[0].rstrip('.xlsx') + '.import.sql', 'w')
    opxreader = opx.OpenPyXlReader(argv[0], 'ID2', errlog=errorlog,
                                   allowed_sheets=['Tabelle1', 'Sheet1'], starting_row=1)
    
    for dat in opxreader.data:
        print dir(dat)
        break
      
    importer = PhenoImporter(opxreader, TROST_DB, errlog=errorlog, sqlout=sqlfile)
    importer.do_import(xml_import=True, real_db_import=False)
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
