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

import OpenPyXl

#class PhenoImporter2(object):
#    def __init__(self, opxreader, db, errlog=sys.stderr, sqlout=sys.stdout):
#        self.data = opxreader.get_data()
#        self.db = db
#        self.errlog = errlog
#        self.sqlout = sqlout
#        self.date_ = opxreader.moddate
#        self.time_ = opxreader.modtime
#        pass
#    def do_import(self, id_anchor, real_db_import=False):
#        C = self.db.cursor()
#        for dobj in self.data:
#            if dobj.is_valid:
#                
#        pass

INSERT_PHENOTYPE = """
INSERT INTO phenotypes 
VALUES (NULL, NULL, '%s', 4, '%s', '00:00:00', NULL, %s, %s, %s); 
""".strip().replace('\n', ' ')

SET_LINKS = """
INSERT INTO %s VALUES (NULL, %i, %s);
""".strip().replace('\n', ' ')

DUMMY_PLANT = """
INSERT INTO plants VALUES (%i, 'DUMMY', 1, 1, NULL, NULL, 'pheno_import_dummy');
""".strip().replace('\n', ' ')

DUMMY_SAMPLE = """
INSERT INTO samples VALUES (%i, NOW());
""".strip().replace('\n', ' ')

DUMMY_LINE = """
INSERT INTO lines VALUES (%i, NOW());
""".strip().replace('\n', ' ')

#
class PhenoImporter(object):
    def __init__(self, opxreader, db, errlog=sys.stderr, sqlout=sys.stdout):
        self.data = opxreader.get_data()
        self.db = db
        self.errlog = errlog
        self.sqlout = sqlout
        self.date_ = opxreader.moddate
        self.time_ = opxreader.modtime
        pass
    def report_sqlerror(self, sqlcmd):
        self.errlog.write('SQL-command (p) failed:\n%s\n' % sqlcmd)
    
    def do_import(self, id_anchor=None, xml_import=False, real_db_import=False):
        C = self.db.cursor()
        print self.data
        for dobj in self.data:
            print dobj
            if dobj.is_valid:
                print 'X'
                if xml_import:
                    commands = OpenPyXl.getsql_from_XML_OpenPyXl(dobj, self.date_, self.time_)
                else:
                    commands = OpenPyXl.getsql_from_OpenPyXl(dobj, self.date_, self.time_, id_anchor)
                for cmd in commands:
                    print cmd
                    if cmd[0] == 'INSERT':
                        sql_cmd = INSERT_PHENOTYPE % cmd[2:]
                    elif cmd[0] == 'LINK':
                        # print cmd
                        sql_cmd = SET_LINKS % cmd[1:]
                    else:
                        continue
                    self.sqlout.write('%s\n' % sql_cmd)
                    if real_db_import:
                        print 'XXX'
                        try:
                            C.execute(sql_cmd)
                            self.db.commit()
                        except:
                            if cmd[0] == 'INSERT':
                                self.db.rollback()
                                self.report_sqlerror(sql_cmd)
                                continue
                            else:
                                self.db.rollback()
                                if cmd[1] == 'phenotype_samples':
                                    aux_cmd = DUMMY_SAMPLE % cmd[2]
                                elif cmd[1] == 'sample_plants':
                                    aux_cmd = DUMMY_PLANT % cmd[3]
                                elif cmd[1] == 'phenotype_lines':
                                    aux_cmd = DUMMY_LINE % cmd[3]
                                else:
                                    self.report_sqlerror(sql_cmd)
                                    continue
                                try:
                                    C.execute(aux_cmd)
                                    self.db.commit()
                                except:
                                    self.db.rollback()
                                    self.report_sqlerror(aux_cmd)
                                    self.report_sqlerror(sql_cmd)    
                                    continue
                                try:
                                    C.execute(sql_cmd)
                                    self.db.commit()
                                except:
                                    self.db.rollback()
                                    self.report_sqlerror(sql_cmd)
                                    continue
                                pass
                            pass
                    pass # if real_db_import
                pass
            pass                                        
        pass
    
    
    def do_import2(self, id_anchor, real_db_import=False):
        # real_db_import = True => actually access the database and do stuff there
        # otherwise just generate sql code
        # ATTENTION: Without actually importing stuff, the phenotype value command will use
        # the wrong phenotype id (in the current case: %i).
        # This is still better than some (highly improbable) race condition, isn't it?
        # This only holds for the generated sql-file, though. The actual database import should 
        # be unaffected.
        db_cursor = self.db.cursor()
        for dobj in self.data:
            if dobj.is_valid:
                commands = dobj.get_sql(self.date_, self.time_, id_anchor)                
                for command_pair in commands:
                    cmd1, cmd2 = command_pair
                    
                    # workaround using dummy samples
                    # dummy_sample = sql.INSERT_DUMMY_SAMPLE % int(getattr(dobj, id_anchor))
                    # self.sqlout.write('%s\n' % dummy_sample)                    
                    
                    # VALUES (NULL, NULL, %s, 4, '%s', '%s', %i, NULL);                    
                    self.sqlout.write('%s\n%s\n' % command_pair)
                    if real_db_import:
                        
                        # workaround using dummy samples
                        # try:
                        #    db_cursor.execute(dummy_sample)
                        #    lastrow = int(db_cursor.lastrowid)
                        #    self.db.commit()
                        #    cmd1 = cmd1 % lastrow
                        #except:
                        #    self.db.rollback()
                        #    self.errlog.write('SQL-command (p) failed:\n%s\n' % \
                        #                      dummy_sample)
                        #    continue
                        
                        try:
                            db_cursor.execute(cmd1)
                            lastrow = int(db_cursor.lastrowid)
                            self.db.commit()
                            cmd2 = cmd2 % lastrow
                        except:
                            self.db.rollback()
                            self.errlog.write('SQL-command (p) failed:\n%s\n' % \
                                              cmd1)
                            continue
                        try:
                            db_cursor.execute(cmd2)
                            self.db.commit()
                        except:
                            self.db.rollback()
                            self.errlog.write('SQL-command (p) failed:\n%s\n' % \
                                              cmd2)
                            self.errlog.write('Previous p-command:\n%s\n' % \
                                              cmd1)
                            continue
                        
            pass
        pass
        
    pass # class
    


def main(argv):
    pass

if __name__ == '__main__': main(sys.argv[1:])