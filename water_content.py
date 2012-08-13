#!/usr/bin/env python

'''
Created on Aug 10, 2012

@author: schudoma
'''

import sys


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
    pass            

def main(argv):
    
    C.execute(WATER_CONTENTS_QUERY)
    
    data = {}
    for row in C.fetchall():
        row_d = dict(zip(FIELDS, row))
        data[row_d['sample_id']] = data.get(row_d['sample_id'], []) + [row_d]
        
        
        
        
    
    # print data[0]
    
    #data_d = {}
    #for 
    #print data.items()[:4]
    for item in data.items():
        if len(item[1]) > 1:
            print item
    
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