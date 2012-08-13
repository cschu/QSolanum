#!/usr/bin/python

import os
import sys
import csv
import time
import math

import openpyxl

import sql
import login
# TROST_DB = login.get_db()

import OpenPyXl as opx
from PhenoImporter import PhenoImporter
"""
ERROR 1452 (23000): Cannot add or update a child row: a foreign key constraint fails (`trost_prod/phenotypes`, CONSTRAINT `fk_phenotypes_samples1` FOREIGN KEY (`sample_id`) REFERENCES `samples` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION)

"""
"""
LASTID in PHENOTYPES: 215937, 28436 rows in set (0.08 sec)

"""

"""
mysql> desc aliquots;
+-------------+--------------+------+-----+---------+----------------+
| Field       | Type         | Null | Key | Default | Extra          |
+-------------+--------------+------+-----+---------+----------------+
| id          | int(11)      | NO   | PRI | NULL    | auto_increment |
| aliquot     | int(11)      | YES  |     | NULL    |                |
| plantid     | int(11)      | YES  |     | NULL    |                |
| sample_date | date         | YES  |     | NULL    |                |
| amount      | int(11)      | YES  |     | NULL    |                |
| amount_unit | varchar(20)  | YES  |     | NULL    |                |
| organ       | varchar(255) | YES  |     | NULL    |                |
+-------------+--------------+------+-----+---------+----------------+
"""



            
#
def read_sample_aliquot_dic(fn):
    sali_d = {}
    first_row = True
    for row in csv.reader(open(fn, 'rb'), 
                          delimiter=',', quotechar='"'):
        print row
        if first_row:
            first_row = False
        else:
            sali_d[int(row[3])] = int(row[0])
    return sali_d



###
def main(argv):    
    
    TROST_DB = login.get_db()
    errorlog = open('carb_import_errors.txt', 'w')
    sqlfile = open('carb_import2012.sql', 'w')
    opxreader = opx.OpenPyXlReader(argv[0], 'SampleID', errlog=errorlog)    
    sali_d = read_sample_aliquot_dic(argv[1])
    
    importer = PhenoImporter(opxreader, TROST_DB, errlog=errorlog, sqlout=sqlfile)
    
    for dobj in importer.data:
        
        try:
            dobj.fSampleID = sali_d[int(dobj.f_SampleID)]
        except:
            errorlog.write('Missing sample: %s\n' % dobj.f_SampleID)
            dobj.is_valid = False
            pass
        
    importer.do_import('f_SampleID')       
    
    sqlfile.close()
    errorlog.close()
    TROST_DB.close()    
    pass



###
def main2(argv):
    ERRORLOG = open('carb_import_errors.txt', 'w')
    #TROST_DB_CURSOR = TROST_DB.cursor()

    fn = argv[0]
    opxreader = opx.OpenPyXlReader(fn, 'SampleID', errlog=ERRORLOG)
    
    sqlfile = open('xxx_carb_import2012.sql', 'w')

    sali_d = read_sample_aliquot_dic(argv[1])
    print sali_d


    count = 0
    for dobj in opxreader.get_data(): #data:
        count += 1
        # print 'XXX',      
        # dobj.is_valid = True
        print dobj.f_SampleID
        try:
            dobj.f_SampleID = sali_d[int(dobj.f_SampleID)]            
        except:
            ERRORLOG.write('Missing sample: %s\n' % dobj.f_SampleID)
            dobj.is_valid = False
            # sys.exit(1)
            pass
        

        if dobj.is_valid:
            print 'VALID', dobj.f_SampleID
            # print dobj.__dict__
            commands = dobj.get_sql(opxreader.moddate, opxreader.modtime, 'f_SampleID')
            print 'COMMANDS:', commands
            # sqlfile.write('%s\n' % '\n'.join(commands))
            # print '\n'.join(commands)
            # break
            
            for command_pair in commands:
                sqlfile.write('%s\n%s\n' % command_pair)
                # continue
                """
                try:
                    TROST_DB_CURSOR.execute(command_pair[0])
                    TROST_DB.commit()
                except:
                    # print TROST_DB_CURSOR.info()
                    TROST_DB.rollback()
                    
                    # print TROST_DB.fetchall()
                    sys.stderr.write('SQL-command (p) failed:\n%s\n' % \
                                         command_pair[0])
                    continue
                    # sys.exit(1)
                    # pass
                try:
                    TROST_DB_CURSOR.execute(command_pair[1])
                    TROST_DB.commit()
                    # print TROST_DB.fetchall()
                except:
                    TROST_DB.rollback()
                    # print TROST_DB.fetchall()
                    sys.stderr.write('SQL-command (pv) failed:\n%s\n' % \
                                         command_pair[1])
                    sys.stderr.write('Previous p-command:\n%s\n' % \
                                         command_pair[0])
                    continue
                """
                # print '\n'.join(commands)

            
            # if count == 3: break
            # break # <-- DEBUG BREAK, CAREFUL!
            pass
        pass
    
    sqlfile.close()
    #TROST_DB.close()
    return None

if __name__ == '__main__': main(sys.argv[1:])
