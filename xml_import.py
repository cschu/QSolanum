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
    date_, time_ = timestamp.split()
    date_ = date_.replace('/', '.')
    date_ = date_.split('.')
    date_ = '-'.join(date_[::-1])
    return date_, time_

dummy = ['NULL', 'NULL', 'LIMS-Aliquot', 'NULL', '2012-10-04', '08:42:41', '1213894', 'NULL', '12', '55', '186.25']

IMPORT_PHENOTYPE = """
INSERT INTO phenotypes
VALUES (%s, %s, '%s', %s, '%s', '%s', %s, %s, %s, %s);
""".strip().replace('\n', ' ')
# (NULL, NULL, 'LIMS-Aliquot', NULL, %s, %s, NULL, %s, %s, %s);

SET_LINKS = """
INSERT INTO %s VALUES (NULL, %i, %i);
""".strip().replace('\n', ' ')

def process_child(node):
    date_, time_ = timestamp2date_time(node.parent.parent.parent.TIMESTAMP)
    data = ['NULL', 'NULL', 'LIMS-Aliquot', 666, 
            date_, time_,            
            'NULL',
            node.parent.parent.ID,
            node.parent.ID,
            node.text,
            node.parent.parent.parent.ID,
            ]
    return tuple(data)
    
def main(argv):
    
    errorlog = open(argv[0]+'_import_errors.txt', 'w')
    
    tree = etree.parse(argv[0])
    root = make_tree(tree.getroot())
    
    nodes = [root]
    while len(nodes) > 0:
        node = nodes.pop()                
        
        if node.is_child():
            row = process_child(node)
            # -1 holds TEST_OBJECT.ID = aliquot_id            
            cmd = IMPORT_PHENOTYPE % row[:-1]            
            try:
                C.execute(cmd)
                lastrow = int(C.lastrowid)
                TROST_DB.commit()                            
            except:
                TROST_DB.rollback()
                errorlog.write('SQL-command (p) failed:\n%s\n' % cmd)
                continue
            cmd = SET_LINKS % ('phenotype_plants', int(row[-1]), lastrow)
            try:
                C.execute(cmd)
                TROST_DB.commit()
            except:
                TROST_DB.rollback()
                errorlog.write('SQL-command (p) failed:\n%s\n' % cmd)
                pass
            # break # debug
            pass        
        else:
            for child in node.children[::-1]:
                nodes.insert(0, child)
        
        pass
    
    errorlog.close()
    pass
    
if __name__ == '__main__': main(sys.argv[1:])
