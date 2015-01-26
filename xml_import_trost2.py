#!/usr/bin/env python
'''
Created on Mar 11, 2014

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys

from lxml import etree

import login

TROST_DB = login.get_db(db='trost_prod')
C = TROST_DB.cursor()

IMPORT_PHENOTYPE = """
INSERT INTO phenotypes
VALUES (%s, '%s', '%s', %s, '%s', '%s', %s, %s, %s, %s);
""".strip().replace('\n', ' ')
SET_LINKS = """
INSERT INTO %s VALUES (NULL, %s, %s);
""".strip().replace('\n', ' ')

SET_DUMMY_PLANT = """
INSERT INTO plants VALUES (%i, 'DUMMY', 1, NULL, NULL, NULL, NULL);
""".strip().replace('\n', ' ')

def timestamp2date_time(timestamp):
    date_, time_ = timestamp.split('T')
    Y, M, D = map(int, date_.split('-'))
    date_ = '%4i-%02i-%02i' % (Y, M, D)
    return date_, time_

def do_import(db, cmd1, cmd2, cmd3, errors):
    cursor = db.cursor()
    try:
        # import phenotype data
        cursor.execute(cmd1)  
        db.commit()                            
    except:
        # if failure: stop import
        db.rollback()
        errors.write('SQL-command (p) failed:\n%s\n' % cmd1)
        return False        
    try:
        # set link to {sample,plant,aliquot} in phenotype_{plants,samples,aliquots}
        cursor.execute(cmd2)
        db.commit()
    except:
        try:
            # if that does not work: add dummy plant 
            cursor.execute(cmd3)
            db.commit()
            print 'Wrote DummyPlant: ' + cmd3
        except:
            db.rollback()
            errors.write('SQL-command (pp) failed:\n%s\n' % cmd2)
            return False
        try:
            # then retry setting the link, this time to the dummy plant
            cursor.execute(cmd2)
            db.commit()
        except:
            # else fail
            db.rollback()
            errors.write('SQL-command (pp) failed:\n%s\n' % cmd2)
            return False
    return True


def main(argv):
    
    errorlog = open(argv[0] + '_import_errors.txt', 'w')
    sqlcmd = open(argv[0] + '_import.sql', 'w')
    
    tree = etree.parse(argv[0])
    nodes = [tree.getroot()]

    currentProgram = 668
    currentVersion = 'NULL'
    date_, time_ = 'NULL', 'NULL'
    limsID = 'NULL'
    entityID, valueID = 'NULL', 'NULL'
    number = None

    while len(nodes) > 0:
        node = nodes.pop()        
        items = dict(node.items())

        print node.tag
        if node.tag.endswith('TESTPROGRAM'):
            currentProgram = int(items['ID'])
            currentVersion = items['VERSION']
        elif node.tag.endswith('TEST_OBJECT'):
            limsID = int(items['ID'])
            date_, time_ = timestamp2date_time(items['TIMESTAMP'])
        elif node.tag.endswith('PARAMETER'):
            entityID = int(items['ID'])
        elif node.tag.endswith('ATTRIBUTE'):
            valueID = int(items['ID'])
        elif node.tag.endswith('VALUE'):
            try:
                number = float(node.text)
            except:
                number = -666.66
                sys.stderr.write('WARNING: limsID=%i. No proper number found. Using satanic dummy!\n' % limsID)
            currentProgram = 668 # need to automatize program updates!
            data = ['NULL', currentVersion, 'LIMS-Aliquot', currentProgram, 
                    date_, time_, 'NULL', entityID, valueID, number]
            print 'LID', limsID, 'DATA', data
            cmd1 = IMPORT_PHENOTYPE % tuple(data)
            sqlcmd.write(cmd1 + '\n')  
            cmd2 = SET_LINKS % ('phenotype_plants', limsID, 'LAST_INSERT_ID()')
            cmd3 = SET_DUMMY_PLANT % limsID
            sqlcmd.write(cmd2 + '\n')
            if do_import(TROST_DB, cmd1, cmd2, cmd3, errorlog):
                continue
            break

        for child in node.getchildren()[::-1]:
            nodes.append(child)
        pass        
    
    sqlcmd.close()
    errorlog.close()    
    TROST_DB.close()
    pass
    
if __name__ == '__main__': main(sys.argv[1:])