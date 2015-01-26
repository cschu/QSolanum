#!/usr/bin/env python
'''
Created on Jul 26, 2013

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys

import OpenPyXl as opx
from PhenoImporter import PhenoImporter

import sql
import login

def main(argv):
    
    """
    ID    VERSION    NAME    OBJECT    OBJECT_TYPE    DESCRIPTION    ID2    TIMESTAMP    MULTIPLICATION    ID3    NAME_E    NAME_D    ID4    ID5    NAME_E6    NAME_D7    ORDER_NUMBER    VALUE    NAME_E8    NAME_D9
                                                                            
   122    180713    TROST2_linecheck    GK-Lines    2        899448    19/07/2013 10:33:21    1    21    plant    Pflanze    0    18    relative size    Relative Groesse    0    1    dwarf    winzig

    """
    
    TROST_DB = login.get_db(db='trost_prod')
    errorlog = open(argv[0].rstrip('.xlsx') + '.sql_errors.txt', 'w')
    sqlfile = open(argv[0].rstrip('.xlsx') + '.import.sql', 'w')
    opxreader = opx.OpenPyXlReader(argv[0], 'LINE_ID', errlog=errorlog, allowed_sheets=['Sheet1'])
    importer = PhenoImporter(opxreader, TROST_DB, errlog=errorlog, sqlout=sqlfile)
    importer.do_import('f_LINE_ID', real_db_import=False)
    sqlfile.close()
    errorlog.close()
    TROST_DB.close() 
    # print [d.get_sql() for d in opxreader.data]
    #for d in opxreader.data: print opx.getsql_from_OpenPyXl(d, 'X', 'Y', 'f_LINE_ID')
        
    
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
