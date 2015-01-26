#!/usr/bin/env python
'''
Created on Sep 3, 2013

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys

import login

import OpenPyXl as opx
from PhenoImporter import PhenoImporter 


LOG_INSERT = "INSERT INTO logger VALUES (NULL,$logger,$channel,$sensor,$startdate,$starttime,$enddate,$endtime);"
LOG_INSERT = "INSERT INTO logger VALUES (NULL,%i,%i,%i,'%s','%s','%s','%s');"
LOG_INSERT = "INSERT INTO logger VALUES (NULL,$logger,$channel,$sensor,$start,$end);"
LOG_INSERT = "INSERT INTO logger VALUES (NULL,%i,%i,%i,'%s','%s');"

P_INSERT = "INSERT INTO phenotypes VALUES (NULL,NULL,'LIMS-Aliquot',4,$date,$time,NULL,21,$value,$logger);"
P_INSERT = "INSERT INTO phenotypes VALUES (NULL,NULL,'LIMS-Aliquot',4,'%s','%s',NULL,21,%i,@last_logger_id);"
PP_INSERT = "INSERT INTO phenotype_plants VALUES (NULL,$plant,LAST_INSERT_ID());"
PP_INSERT = "INSERT INTO phenotype_plants VALUES (NULL,%i,LAST_INSERT_ID());"
#INSERT INTO phenotypes VALUES (NULL,NULL,'LIMS-Aliquot',4,$date,$time,NULL,-180181,295,$logger);
#INSERT INTO phenotype_plants VALUES (NULL,$plant,LAST_INSERT_ID());

def convert_date(date):
    d, m, Y = date.split('.')
    return '-'.join([Y, m, d])
    

def import_loggerdata(fn):
    headers = None
    
    print 'START TRANSACTION;'
    print 'SET autocommit = 0;'
    
    for line in open(fn):
        line = line.strip().split('\t')
        if headers is None:
            headers = line
            continue
        # 1    1    1    16.08.2011    14:05:57    28.10.2011    16:05:57    MPI_Test_1_2    48656    1074696    [St.Alegria.n].270    drought    Alegria
        ints = tuple(map(int, line[:3]))
        # dt_strings = (convert_date(line[3]), line[4], convert_date(line[5]), line[6])        
        dt_strings = (' '.join([convert_date(line[3]), line[4]]), ' '.join([convert_date(line[5]), line[6]]))
        print LOG_INSERT % (ints + dt_strings)
        print 'SET @last_logger_id = LAST_INSERT_ID();'
        print P_INSERT % (tuple(dt_strings[0].split(' ')) + (294,))
        print PP_INSERT % int(line[9])
        print P_INSERT % (tuple(dt_strings[1].split(' ')) + (295,))
        print PP_INSERT % int(line[9])
        
    print 'COMMIT;'
    pass





def read_lookup_table(fn):
    headers = None
    lut = {}
    for line in open(fn):
        line = line.strip().split('\t')
        if headers is None:
            headers = line
            continue
        # careful: if same (logger, sensor, channel) @ same date, there's a key clash
        # right now this works. 
        key = tuple(map(int, line[:3])) + (line[3:7], )
        lut[key] = dict(zip(headers[3:], line[3:]))
    return lut

        
    


            
def read_loggerdata(fn, lut, loggerID):
    headers = None
    data = []   
    for line in open(fn):
        line = line.strip().split('\t')
        if headers is None:
            headers = line
            continue
        date_, time_ = line[0].split('_')
        values = dict(zip(headers[1:], line[1:]))
    
    


###
def main(argv):
    
    #lut = read_lookup_table(argv[0])
    #print len(lut)
    # for k, v in sorted(lut.items()): print k, v
    import_loggerdata(argv[0])
    
    
    
    
        
    
    """
    TROST_DB = login.get_db(db='trost_prod')
    errorlog = open(argv[0].rstrip('.xlsx') + '.sql_errors.txt', 'w')
    sqlfile = open(argv[0].rstrip('.xlsx') + '.import.sql', 'w')
    opxreader = opx.OpenPyXlReader(argv[0], 'AliquotID', errlog=errorlog,
                                   allowed_sheets=['Tabelle1', 'Sheet1'])    
    #print 'x'
    importer = PhenoImporter(opxreader, TROST_DB, errlog=errorlog, sqlout=sqlfile)
    importer.do_import('f_AliquotID', real_db_import=True)
    # print 'y'
    #try:
    #    importer.do_import('f_Plant_ID', real_db_import=True)       
    #except:
    #    print 'GRRRR'

    sqlfile.close()
    errorlog.close()
    TROST_DB.close()
    """    
    pass



def main2(argv):
    
    TROST_DB = login.get_db(db='trost_prod_new')
    errorlog = open('carb_import_errors.txt', 'w')
    
    
    sqlfile = open('carb_excel_lmu_import_2012.sql', 'w')
    opxreader = opx.OpenPyXlReader(argv[0], 'SampleID', errlog=errorlog,
                                   allowed_sheets=['Ergebnisse'])    
    # return None
    
    
    importer = PhenoImporter(opxreader, TROST_DB, errlog=errorlog, sqlout=sqlfile)
    importer.do_import('f_SampleID', real_db_import=True)  
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
