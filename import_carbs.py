#!/usr/bin/python

import os
import sys
import csv
import time
import math

import openpyxl

import login
TROST_DB = login.get_db()

cast_d = {'s': str, 'n': float}

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

MYSQL_PHENOTYPE_VALUES = """
INSERT INTO phenotype_values 
(id, value_id, phenotype_id, number)
SELECT NULL, %i, phenotypes.id, %f
FROM phenotypes
WHERE phenotypes.sample_id = %i;
""".strip()

INSERT_PHENOTYPE = """
INSERT INTO phenotypes
(id, version, object, program_id, date, time, sample_id, invalid)
SELECT NULL, NULL, 'LIMS-Aliquot', 4, '%s', '%s', aliquots.id, NULL
FROM aliquots
WHERE aliquots.aliquot = %i;
""".strip().replace('\n', ' ')

INSERT_PHENOTYPE_VALUE = """
INSERT INTO phenotype_values
(id, value_id, phenotype_id, number)
SELECT NULL, %i, phenotypes.id, %f 
FROM phenotypes
WHERE phenotypes.id in 
(SELECT MAX(phenotypes.id) FROM phenotypes);
""".strip().replace('\n', ' ')

ERRORLOG = open('carb_import_errors.txt', 'w')

#
class OpenPyXl_Object(object):
    def __init__(self, fields, dtypes, values, casts=cast_d):
        self.fields = ['f_' + str(field) 
                       for field in fields]
        self.is_valid = True
        # if not field is None]
        for i, field in enumerate(self.fields): 
            print field, field == 'f_None', '->', values[i], '<-'
            if field != 'f_None':
                try:
                    print '>>', field, cast_d[dtypes[i]](values[i])
                    setattr(self, field, cast_d[dtypes[i]](values[i]))
                except:
                    ERRORLOG.write('%s: %s = %s\n' % (self.f_SampleID,
                                                      field,
                                                      str(values[i])))
                    self.is_valid = False
                    pass
        pass
    def get_sql(self, date_='CURDATE()', time_='CURTIME()'):
        sqlcmd = []            
        print 'SID', type(self.f_SampleID)
        for field in self.fields:
            if field not in ['f_SampleID', 'f_None']:
                print '!', field, getattr(self, field)
                print type(getattr(self, field))

                sqlcmd.append((INSERT_PHENOTYPE % (date_, time_,
                                                   int(self.f_SampleID)),
                               INSERT_PHENOTYPE_VALUE % \
                                   (int(field.lstrip('f_')),
                                    getattr(self, field))))
                """
                sqlcmd.append(INSERT_PHENOTYPE % (date_, time_,
                                                  int(self.f_SampleID)))
                sqlcmd.append(INSERT_PHENOTYPE_VALUE % \
                                  (int(field.lstrip('f_')),
                                   getattr(self, field)))
                """
                # sqlcmd.append(MYSQL_PHENOTYPE_VALUES % \
                #                  (int(field.lstrip('f_')),
                #                   getattr(self, field),
                #                   int(self.f_SampleID)))
        # return '\n'.join(sqlcmd)
        return sqlcmd
    pass
            
#
def read_sample_aliquot_dic(fn):
    sali_d = {}
    first_row = True
    for row in csv.reader(open(fn, 'rb'), 
                          delimiter=',', quotechar='"'):
        if first_row:
            first_row = False
        else:
            sali_d[int(row[3])] = int(row[0])
    return sali_d

#
def process_sheet(sheet):
    header = [cell.value for cell in sheet.rows[0]]
    dtypes = [cell.data_type for cell in sheet.rows[0]]
    print header, 'SampleID' in header
    if not 'SampleID' in header:
        sys.stderr.write('No header line: Aborting.\n')
        sys.exit(1)
    
    data = []
    for row in sheet.rows[2:]:
        row_data = [cell.value for cell in row]
        row_dtypes = [cell.data_type for cell in row]
        dobj = OpenPyXl_Object(header, dtypes, row_data)
        # print dobj.__dict__
        # print dobj.get_sql()
        data.append(dobj)
    return data

#
def read_xlsx(fn):
    wb = openpyxl.reader.excel.load_workbook(filename=fn)
    all_sheets = wb.get_sheet_names()
    print all_sheets
    data = []

    for sheet in all_sheets:
        if sheet == 'Pivottabelle': 
            continue
        data += process_sheet(wb.get_sheet_by_name(sheet))
    return data
        
    pass

def get_modification_time(fn):
    return time.strftime('%Y-%m-%d %H:%M:%S', 
                         time.gmtime(os.path.getmtime(fn)))



###
def main(argv):

    TROST_DB_CURSOR = TROST_DB.cursor()

    fn = argv[0]
    data = read_xlsx(fn)
    moddate, modtime = get_modification_time(fn).split()
    
    sqlfile = open('carb_import2012.sql', 'w')

    sali_d = read_sample_aliquot_dic(argv[1])

    count = 0
    for dobj in data:
        count += 1
        # print 'XXX',      
        # dobj.is_valid = True
        try:
            dobj.f_SampleID = sali_d[int(dobj.f_SampleID)]            
        except:
            ERRORLOG.write('Missing sample: %s\n' % dobj.f_SampleID)
            dobj.is_valid = False
            # sys.exit(1)
            pass
        

        if dobj.is_valid:
            # print dobj.__dict__
            commands = dobj.get_sql(date_=moddate, time_=modtime)
            # sqlfile.write('%s\n' % '\n'.join(commands))
            # print '\n'.join(commands)
            # break
            
            for command_pair in commands:
                sqlfile.write('%s\n%s\n' % command_pair)
                # continue
                
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
                # print '\n'.join(commands)

            
            # if count == 3: break
            # break # <-- DEBUG BREAK, CAREFUL!
            pass
        pass
    
    sqlfile.close()
    TROST_DB.close()
    return None

if __name__ == '__main__': main(sys.argv[1:])
