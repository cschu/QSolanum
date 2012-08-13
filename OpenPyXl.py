#!/usr/bin/env python

'''
Created on Aug 9, 2012

@author: schudoma
'''

import os
import sys
import time

import openpyxl

import sql
cast_d = {'s': str, 'n': float}

ALLOWED_SHEETS = ['Ergebnisse', 'ParzellenernteZuechter', 'ParzellenernteExperimente']

class OpenPyXlObject(object):
    def __init__(self, fields, dtypes, values, errlog=sys.stderr, casts=cast_d):
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
                    errlog.write('%s: %s = %s\n' % (self.f_SampleID,
                                                    field,
                                                    str(values[i])))
                    self.is_valid = False
                    pass
        pass
    
    
    def get_sql(self, date_, time_, id_field):
        sqlcmd = []
        for field in self.fields:
            if field not in [id_field, 'f_None']:
                print '!', field, getattr(self, field), type(getattr(self, field))                
                try:
                    sqlcmd.append((sql.INSERT_PHENOTYPE % (date_, time_,
                                                           int(getattr(self, id_field))),
                                   sql.INSERT_PHENOTYPE_VALUE % \
                                     (int(field.lstrip('f_')),
                                      getattr(self, field),
                                      '%i')))
                except:
                    self.is_valid = False
                    pass
        return sqlcmd
    pass


class OpenPyXlReader(object):
    def __init__(self, fn, id_anchor, errlog=sys.stderr, allowed_sheets=ALLOWED_SHEETS):
        self.data = []
        self.errlog = errlog
        self.moddate, self.modtime = OpenPyXlReader.get_modification_time(fn)        
        wb = openpyxl.reader.excel.load_workbook(filename=fn)
        for sheet in wb.get_sheet_names():
            if sheet in allowed_sheets:
                self.data += self.process_sheet(wb.get_sheet_by_name(sheet), id_anchor)
                            
        pass    
    def process_sheet(self, sheet, id_anchor):
        header = [cell.value for cell in sheet.rows[0]]
        if not id_anchor in header:
            sys.stderr.write('No header line: Aborting.\n') 
            sys.exit(1)    
        sheet_data = []
        for row in sheet.rows[2:]:
            row_data = [cell.value for cell in row]
            row_dtypes = [cell.data_type for cell in row]
            dobj = OpenPyXlObject(header, row_dtypes, row_data, errlog=self.errlog)
            sheet_data.append(dobj)
        return sheet_data
    def get_data(self):
        return self.data
    def get_modtime(self):
        return self.modtime
    def get_moddate(self):
        return self.moddate
    @staticmethod
    def get_modification_time(fn):
        return time.strftime('%Y-%m-%d %H:%M:%S', 
                             time.gmtime(os.path.getmtime(fn))).split()


