#!/usr/bin/env python

import os
import sys
import csv
import time
import math

import openpyxl

import sql
import login


import OpenPyXl as opx
from PhenoImporter import PhenoImporter 


###
def main(argv):    
    
    TROST_DB = login.get_db()
    errorlog = open('starch_import_errors.txt', 'w')
    sqlfile = open('starch_excel_import_2012.sql', 'w')
    opxreader = opx.OpenPyXlReader(argv[0], 'Plant_ID', errlog=errorlog)    
    # print 'x'
    importer = PhenoImporter(opxreader, TROST_DB, errlog=errorlog, sqlout=sqlfile)
    # print 'y'
    try:
        importer.do_import('f_Plant_ID', real_db_import=True)       
    except:
        print 'GRRRR'

    sqlfile.close()
    errorlog.close()
    TROST_DB.close()    
    pass

if __name__ == '__main__': main(sys.argv[1:])
