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


WATER_CONTENTS_QUERY = """
SELECT
P1.sample_id AS sample_id,
P1.id AS p1_id, P1.date AS p1_date,
PV1.*, PE1.entity_id AS pe1_entity_id,
P2.id AS p2_id, P2.date AS p2_date,
PV2.*, PE2.entity_id AS pe2_entity_id
FROM
phenotypes AS P1
LEFT JOIN phenotypes AS P2
ON P1.sample_id = P2.sample_id
LEFT JOIN phenotype_values AS PV1
ON P1.id = PV1.phenotype_id
LEFT JOIN phenotype_values AS PV2
ON P2.id = PV2.phenotype_id
LEFT JOIN phenotype_entities AS PE1
ON P1.id = PE1.phenotype_id
LEFT JOIN phenotype_entities AS PE2
ON P2.id = PE2.phenotype_id
WHERE
P1.id != P2.id AND
P1.object = 'LIMS-Aliquot' AND P2.object = 'LIMS-Aliquot' AND
PV1.value_id IN  (55,156,69,163,164) AND
PV2.value_id IN  (55,156,69,163,164) AND
PV1.value_id != PV2.value_id AND
(PV1.value_id = 55 OR (PV1.value_id = 69 AND PV2.value_id != 55))
ORDER BY sample_id, P1.date, P2.date;
""".strip().replace('\n', ' ')

FIELDS = ['sample_id', 'p1_id', 'p1_date', 
          'pv1_id', 'pv1_value_id', 'pv1_phenotype_id', 'pv1_number', 'pe1_entity_id',
          'p2_id', 'p2_date',
          'pv2_id', 'pv2_value_id', 'pv2_phenotype_id', 'pv2_number', 'pe2_entity_id']

def compute_rwc(data):
    candidate_69 = None
    candidate_156 = None
    for row in sorted(data, key=lambda x:x['delta_t']):
        if row['pv2_id'] == 69 and row['delta_t'] >= 2 and row['delta_t'] <= 7:
            if candidate_69 is None:
                candidate_69 = row
            else:
                print 'Duplicate value (69):'
                print 'Original:', candidate_69
                print 'Duplicate:', row
        elif row['pv2_id'] == 156 and row['delta_t'] >= 1 and row['delta_t'] <= 2:
            if candidate_156 is None:
                candidate_156 = row
            else:
                print 'Duplicate value (156):'
                print 'Original:', candidate_156
                print 'Duplicate:', row
        pass
    """
    if len(candidates_69) > 1:
        print 'Duplicate 69', 
        candidates_69 = sorted(candidates_69, key=lambda x:x['delta_t'])
    if len(candidates_156) > 1:
        candidates_156 = sorted(candidates_156, key=lambda x:x['delta_t'])
    """
    return None

def compute_stuff(data):
    #delta_t = []     
    for i, row in enumerate(data):         
        data[i]['delta_t'] = row['p2_date'] - row['p1_date']
    data_55 = [row for row in data if row['pv1_id'] == 55 and row['delta_t'] > 0]
    compute_rwc(data_55)
    
    pass            


def main(argv):
    
    C.execute(WATER_CONTENTS_QUERY)
    
    fo = open('water_contents.csv', 'w')
    fo.write('%s\n' % (';'.join(FIELDS)))
    fo.write('thing\n')
    for row in C.fetchall():
        fo.write('%s\n' % (';'.join(map(str, row))))
    fo.close()
    return None

    data = {}
    for row in C.fetchall():
        row_d = dict(zip(FIELDS, row))
        data[row_d['sample_id']] = data.get(row_d['sample_id'], []) + [row_d]
    for key in data:
        if len(data[key]) == 1:
            del data[key]
        else:
            compute_stuff(data[key])
        pass      

        
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
