#!/usr/bin/env python
'''
Created on Oct 18, 2012

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys

import login

import OpenPyXl as opx
from PhenoImporter import PhenoImporter 

###
def main(argv):    
    
    TROST_DB = login.get_db(db='trost_prod_reimport')
    errorlog = open(argv[0].rstrip('.xlsx') + '.sql_errors.txt', 'w')
    sqlfile = open(argv[0].rstrip('.xlsx') + '.import.sql', 'w')
    opxreader = opx.OpenPyXlReader(argv[0], 'Sample_ID', errlog=errorlog,
                                   allowed_sheets=['JKIShelter2012', 'JKIGWH2012', 'JKIFeld2012',
                                                   'Boehlendorf2012'])    
    # print 'x'
    importer = PhenoImporter(opxreader, TROST_DB, errlog=errorlog, sqlout=sqlfile)
    importer.do_import('f_Sample_ID', real_db_import=True)
    # print 'y'
    #try:
    #    importer.do_import('f_Plant_ID', real_db_import=True)       
    #except:
    #    print 'GRRRR'

    sqlfile.close()
    errorlog.close()
    TROST_DB.close()    
    pass



def main2(argv):
    
    TROST_DB = login.get_db(db='trost_prod_new')
    errorlog = open('dw_import_errors.txt', 'w')
    
    
    sqlfile = open('dw_excel_jki_import_2012.sql', 'w')
    opxreader = opx.OpenPyXlReader(argv[0], 'Sample_ID', errlog=errorlog,
                                   allowed_sheets=['JKIShelter2012', 'JKIGWH2012', 'JKIFeld2012'])    
    # return None
    
    
    importer = PhenoImporter(opxreader, TROST_DB, errlog=errorlog, sqlout=sqlfile)
    importer.do_import('f_Sample_ID', real_db_import=True)  
    #return None
    #try:
    #    importer.do_import('f_Sample_ID', real_db_import=False)       
    #except:
    #    print 'GRRRR'

    sqlfile.close()
    errorlog.close()
    TROST_DB.close()    
    pass

if __name__ == '__main__': main(sys.argv[1:])
