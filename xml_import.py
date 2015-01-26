#!/usr/bin/env python
'''
Created on Oct 10, 2012

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys

from lxml import etree

import login
# from starch_report import TROST_DB
TROST_DB = login.get_db(db='trost_prod')
C = TROST_DB.cursor()


class Node(object):
    def __init__(self, tag, items, parent=None):
        self.tag = tag
        self.parent = parent
        # print 'I am', self.tag, 'my parent is', parent
        for item in items:
            setattr(self, item[0], item[1])
        self.children = []
        
        self.text = None
        pass
    def is_child(self):
        return len(self.children) == 0
    pass
    
def make_tree(xmlnode, parent=None):
    # print 'MT:', xmlnode.tag,
    # if parent is not None:
    #    print parent.tag
    #else:
    #    print '<None>'
    node = Node(xmlnode.tag, xmlnode.items(), parent=parent)
    for child in xmlnode.getchildren():
        node.children.append(make_tree(child, parent=node))
    if len(node.children) == 0:
        node.text = xmlnode.text
    return node

def timestamp2date_time(timestamp):
    date_, time_ = timestamp.split('T')
    Y, M, D = map(int, date_.split('-'))
    date_ = '%4i-%02i-%02i' % (Y, M, D)
    # time_ = '%02i:%02i:%02i' % (hh, mm, ss)
    return date_, time_, False

def timestamp2date_time_old(timestamp):
    # sys.stderr.write("$$%s$$\n" % timestamp)
    dtdata = timestamp.split()    
    date_, time_ = dtdata[:2]
    slash_warning = False
    
    is_ampm = len(dtdata) == 3 and dtdata[2].strip().upper() in ['AM', 'PM']
    
    if '/' in date_:
        # either German D/M/Y or American M/D/Y
        # target format is YYYY-MM-DD
        D, M, Y = map(int, date_.split('/'))
        
        if is_ampm:
            # D/M/Y format, swap D and M
            M, D = D, M
            slash_warning = True        
    else:
        D, M, Y = map(int, date_.split('.')) 
    
    date_ = '%4i-%02i-%02i' % (Y, M, D)
    
    """
    if '/' in date_:        
        # M/D/Y format (OR D/M/Y format ><;)
        # M, D, Y = map(int, date_.replace('/', '.').split('.'))
        M, D, Y = map(int, date_.split('/'))
        if M > 12:            
            # if M <= 12 it still might be the day... ><;
            M, D = D, M
        elif D < 13 and (D != M):
            # if M <= 12 and D < 13 and D != M: cannot decide which one is which (D==M is trivial)
            slash_warning = True
        date_ = '%4i-%02i-%02i' % (Y, M, D)
    else:        
        # DD.MM.YYYY format
        date_ = '-'.join(date_.split('.')[::-1])
    """
    
    # 12am = 0:00, 12pm = 12:00
    if is_ampm:
        hh, mm, ss = map(int, time_.split(':'))
        am_or_pm = dtdata[2].strip().upper()
        if hh == 12 and mm in xrange(0, 60) and am_or_pm == 'AM':
            hh = 0
        elif (hh in xrange(1, 12) and mm in xrange(0, 60) and am_or_pm == 'AM'):
            pass
        elif (hh == 12 and mm in xrange(1, 60) and am_or_pm == 'PM'):
            pass
        elif (hh in xrange(1, 12) and mm in xrange(0, 60) and am_or_pm == 'PM'):
            hh += 12
        time_ = '%02i:%02i:%02i' % (hh, mm, ss)
        
    if slash_warning:
        pass
        #sys.stderr.write("$$%s$$\n" % timestamp)
        #sys.stderr.write("$$%s %s %s$$\n" % (date_, time_, slash_warning))
    
    return date_, time_, slash_warning

dummy = ['NULL', 'NULL', 'LIMS-Aliquot', 'NULL', '2012-10-04', '08:42:41', '1213894', 'NULL', '12', '55', '186.25']

IMPORT_PHENOTYPE = """
INSERT INTO phenotypes
VALUES (%s, %s, '%s', %s, '%s', '%s', %s, %s, %s, %s);
""".strip().replace('\n', ' ')
# (NULL, NULL, 'LIMS-Aliquot', NULL, %s, %s, NULL, %s, %s, %s);

SET_LINKS = """
INSERT INTO %s VALUES (NULL, %s, %s);
""".strip().replace('\n', ' ')



def process_child(node):
    
    try:
        timestamp = node.parent.parent.parent.TIMESTAMP
    except:
        timestamp = node.parent.parent.parent.parent.TIMESTAMP
    
        
    date_, time_, slash_warning = timestamp2date_time(timestamp)
    print date_, time_, slash_warning, timestamp
    
    program_id = 666
    if slash_warning:
        program_id = 888
    
    # print node.parent.parent, dir(node.parent.parent), node.parent.parent.tag
    if node.parent.parent.tag.upper() == 'PARAMETER':
        entity_id = node.parent.parent.ID
        link_id = node.parent.parent.parent.ID
    else:
        entity_id = node.parent.parent.parent.ID
        link_id = node.parent.parent.parent.parent.ID
    
    # value = node.text
    
    data = ['NULL', 'NULL', 'LIMS-Aliquot', program_id,
            date_, time_,            
            'NULL',
            entity_id,
            node.parent.ID,
            node.text,
            link_id
            ]
    print data
    return data
    
def main(argv):
    
    errorlog = open(argv[0] + '_import_errors.txt', 'w')
    sqlcmd = open(argv[0] + '_import.sql', 'w')
    
    tree = etree.parse(argv[0])
    root = make_tree(tree.getroot())
    
    is_bbch_file = 'BBCH' in root.NAME.upper()
    #print root.NAME
    #sys.exit(1)
    
    nodes = [root]
    while len(nodes) > 0:
        node = nodes.pop()                
        
        if node.is_child():
            row = process_child(node)
            # break
           
            bbch = None
            if int(row[8]) == 221:
                bbch = row[9]   
                if bbch == 'NULL':
                    # no BBCH determined: ignore entry 
                    continue
                row[9] = 'NULL'
            # sqlcmd.write('ROW: ' + ' '.join(map(str, row)) + 'BBCH:' + str(bbch) + '\n')
            # -1 holds TEST_OBJECT.ID or SAMPLE.ID = aliquot_id            
            cmd = IMPORT_PHENOTYPE % tuple(row[:-1])
            sqlcmd.write(cmd + '\n')                                     
            
            # continue

            try:
                # print cmd
                C.execute(cmd)  
                lastrow = int(C.lastrowid)             
                TROST_DB.commit()                            
            except:
                TROST_DB.rollback()
                errorlog.write('SQL-command (p) failed:\n%s\n' % cmd)
                continue
            
            cmd = SET_LINKS % ('phenotype_plants', str(row[-1]), str(lastrow))
            sqlcmd.write(cmd + '\n')
            try:
                C.execute(cmd)
                TROST_DB.commit()
            except:
                TROST_DB.rollback()
                errorlog.write('SQL-command (pp) failed:\n%s\n' % cmd)
                pass
            
            continue

            #if is_bbch_file:
            if bbch is not None:                            
                cmd = SET_LINKS % ('phenotype_bbches', str(lastrow), str(bbch))
                sqlcmd.write(cmd + '\n') 
                try:
                    C.execute(cmd)
                    TROST_DB.commit()
                except:
                    TROST_DB.rollback()
                    errorlog.write('SQL-command (pb) failed:\n%s\n' % cmd)
                    pass
                pass            
            # break # debug
            pass
                    
        else:
            for child in node.children[::-1]:
                nodes.insert(0, child)
        
        pass
    
    sqlcmd.close()
    errorlog.close()
    
    TROST_DB.close()
    pass
    
if __name__ == '__main__': main(sys.argv[1:])
