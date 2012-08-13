#!/usr/bin/env python

'''
Created on Aug 10, 2012

@author: schudoma
'''

import sys
import datetime

import login
TROST_DB = login.get_db()
C = TROST_DB.cursor()


WATER_CONTENTS_QUERY = """ 
select 
phenotypes.id as pheno_id,
phenotype_values.number as pv_number,
`values`.id as value_id,
`values`. value,
phenotypes.sample_id,
phenotypes.date,
phenotypes.time,
entities.id as entity_id
from phenotypes, phenotype_values, `values`, phenotype_entities, entities
where 
phenotypes.id = phenotype_values.phenotype_id and 
`values`.id = phenotype_values.value_id and 
phenotype_values.value_id in (55,156,69,163,164) and 
object = 'LIMS-Aliquot' and 
phenotype_entities.phenotype_id = phenotypes.id and 
phenotype_entities.entity_id = entities.id and 
entities.id in (366,12);
""".strip().replace('\n', ' ')

FIELDS = ['pheno_id', 'pv_number', 'value_id', 'value', 'sample_id', 'date', 'time', 'entity_id']


def compute_stuff(data):
    for key, val in data.items():
        print key 
        print '\n'.join(map(str, [item 
                                  for item in val 
                                  if item['value_id'] == 55]))

        pass
    return None            

def find_next_pos(data, field, value, start=0):
    for i in xrange(start, len(data)):
        if data[i][field] == value:
            return i
    return -1

def find_all_pos(data, field, value):
    return [i for i, item in enumerate(data)
            if item[field] == value]

def compute_stuff(data):
    for item in find_all_pos(data, 'value_id', 55):
        

def main(argv):
    
    C.execute(WATER_CONTENTS_QUERY)
    
    data = {}
    for row in C.fetchall():
        row_d = dict(zip(FIELDS, row))
        data[row_d['sample_id']] = data.get(row_d['sample_id'], []) + [row_d]
        
    print len(data)
    for key in data.keys():
        if len(data[key]) == 1:
            del data[key]
        else:
            data[key] = sorted(data[key], key=lambda x:x['date'])
            print '\n'.join(map(str, data[key]))
            break
    print len(data)
        
    # result = compute_stuff(data)    
    
        
    """
    fw_data = [row for row in data if row['value_id'] == 55]
    sw_data = [row for row in data if row['value_id'] == 156]
    dw_data = [row for row in data if row['value_id'] == 69]
    tara_data = [row for row in data if row['value_id'] == 163]
    fwb_data = [row for row in data if row['value_id'] == 164]
    
    sw_data = sorted(sw_data, key=lambda x:(x['sample_id'], x['date'], x['time']))
    print sw_data[:4]
    print len(data), len(fw_data) + len(sw_data) + len(dw_data) + len(tara_data) + len(fwb_data)
    """
    
    
    # print C.fetchall()
    
    
    
    
    
    TROST_DB.close()
    pass


if __name__ == '__main__': main(sys.argv[1:])
