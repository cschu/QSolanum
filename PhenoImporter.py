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
    def do_import(self, id_anchor, real_db_import=False):
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
                    self.sqlout.write('%s\n%s\n' % command_pair)
                    if real_db_import:
                        
                        try:
                            db_cursor.execute(command_pair[0])
                            lastrow = int(db_cursor.lastrowid)
                            self.db.commit()
                        except:
                            self.db.rollback()
                            self.errlog.write('SQL-command (p) failed:\n%s\n' % \
                                              command_pair[0])
                            continue
                        try:
                            db_cursor.execute(command_pair[1] % lastrow)
                            self.db.commit()
                        except:
                            self.db.rollback()
                            self.errlog.write('SQL-command (p) failed:\n%s\n' % \
                                              command_pair[1] % lastrow)
                            self.errlog.write('Previous p-command:\n%s\n' % \
                                              command_pair[0])
                            continue
            pass
        pass
        
    pass # class
    


def main(argv):
    pass

if __name__ == '__main__': main(sys.argv[1:])