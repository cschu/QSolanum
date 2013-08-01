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

ALLOWED_SHEETS = ['Ergebnisse', 'ParzellenernteZuechter', 'ParzellenernteExperimente', 'ALL_IMPORT',
                  'Parzellenernte_Experimente']

def get_limsobject(string):
    string = string.lower()
    if 'plant' in string or 'aliquot' in string:
        return 'LIMS-Aliquot'
    elif 'sample' in string:
        return 'LIMS-Sample'
    elif 'line' in string:
        return 'LIMS-Line'
    else:
        return 'unknown'

def getsql_from_XML_OpenPyXl(obj, date_, time_):
    #sql_commands = []
    f_entity = int(obj.f_ID3)
    f_date = obj.f_TIMESTAMP.split()[0].replace('/', '-')
    # hardcoded for now!
    linktable = 'phenotype_lines'
    value_id = obj.f_ID5
    number = obj.f_VALUE
    cmd1 = ('INSERT', 'phenotypes', 'LIMS-Aliquot', f_date, f_entity, value_id, number)
    cmd2 = ('LINK', linktable, obj.f_ID2, 'LAST_INSERT_ID()')
    return [cmd1, cmd2]
    
#        
def getsql_from_OpenPyXl(obj, date_, time_, id_field):
    sql_commands = []    
    plant_links = []
    if 'f_Entity' in obj.fields:        
        f_entity = int(getattr(obj, 'f_Entity'))    
    else:
        f_entity = '-180181'
    if 'f_Date' in obj.fields:
        f_date = getattr(obj, 'f_Date').split()[0]
    else:
        f_date = date_
    f_obj = get_limsobject(id_field)
    if f_obj == 'LIMS-Aliquot':
        if 'plant' in id_field.lower():
            ## not sure if this works with older data, e.g. the JKI-trials
            linktable = 'phenotype_plants'
        else:
            linktable = 'phenotype_aliquots'
    elif f_obj == 'LIMS-Sample':
        linktable = 'phenotype_samples'
    elif f_obj == 'LIMS-Line':
        linktable = 'phenotype_lines'
    else:
        linktable = None
    f_id = int(getattr(obj, id_field))
        
    for field in obj.fields:
        if field not in [id_field, 'f_None', 'f_Entity', 'f_Date']:
            if not field.startswith('f_link'):
                value = getattr(obj, field) 
                print 'VALUE=', value, value is None, isinstance(value, str)
                if value == 'None':
                    value = 'NULL'
                cmd1 = ('INSERT', 'phenotypes', f_obj, f_date, f_entity, field.lstrip('f_'), value)
                sql_commands.append(cmd1)
                if linktable is not None:
                    cmd2 = ('LINK', linktable, f_id, 'LAST_INSERT_ID()')
                    sql_commands.append(cmd2)
                #if value != 'None':             
                #    cmd1 = ('INSERT', 'phenotypes', f_obj, f_date, f_entity, field.lstrip('f_'), value)
                #    sql_commands.append(cmd1)
                #    if linktable is not None:
                #        cmd2 = ('LINK', linktable, f_id, 'LAST_INSERT_ID()')
                #        sql_commands.append(cmd2)
            else:
                link = ('LINK', 'sample_plants', f_id, int(getattr(obj, field)))
                plant_links.append(link)
    return sql_commands + plant_links
    
    
         


class OpenPyXlObject(object):
    def __init__(self, fields, dtypes, values, identifier,
                 errlog=sys.stderr, casts=cast_d):
        self.fields = ['f_' + str(field) 
                       for field in fields]
        self.id_ = identifier
        self.is_valid = True
        # if not field is None]
        for i, field in enumerate(self.fields): 
            print field, field == 'f_None', '->', values[i], '<-'
            if field != 'f_None':
                cast_ = cast_d[dtypes[i]]
                if field == 'f_Date':
                    cast_ = str                
                try:
                    print '>>', field, cast_(values[i])                    
                    setattr(self, field, cast_(values[i]))
                except:
                    err_par = (getattr(self, self.id_), field, str(values[i]))
                    errlog.write('%s: %s = %s\n' % err_par)
                    self.is_valid = False
                    pass
        print 'SELf.isvalid=', self.is_valid
        pass
    
    
    
    
    # # VALUES (NULL, NULL, %s, 4, '%s', '%s', %i, NULL);
    def get_sql(self, date_, time_, id_field):
        sqlcmd = []
        for field in self.fields:
            if field not in [id_field, 'f_None']:
                # print '!', field, getattr(self, field), type(getattr(self, field))                
                try:
                    # %i: int(getattr(self, id_field)) -- workaround
                    # old command in INSERT_PHENOTYPE_PREDB
                    sqlcmd.append((sql.INSERT_PHENOTYPE % ("'%s'" % get_limsobject(id_field), 
                                                           date_, time_, 
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
    def __init__(self, fn, id_anchor, errlog=sys.stderr, allowed_sheets=ALLOWED_SHEETS, starting_row=2):
        self.data = []
        self.errlog = errlog
        self.moddate, self.modtime = OpenPyXlReader.get_modification_time(fn)        
        wb = openpyxl.reader.excel.load_workbook(filename=fn)
        for sheet in wb.get_sheet_names():
            if sheet in allowed_sheets:
                self.data += self.process_sheet(wb.get_sheet_by_name(sheet), id_anchor, starting_row=starting_row)
                            
        pass    
    def process_sheet(self, sheet, id_anchor, starting_row=2):
        header = [cell.value for cell in sheet.rows[0]]
        if not id_anchor in header:
            sys.stderr.write('No header line: Aborting.\n') 
            sys.exit(1)    
        sheet_data = []
        for row in sheet.rows[starting_row:]:
            row_data = [cell.value for cell in row]
            if str(row_data[0]).startswith('#'):
                continue
            row_dtypes = [cell.data_type for cell in row]
            dobj = OpenPyXlObject(header, row_dtypes, row_data, id_anchor, errlog=self.errlog)
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


