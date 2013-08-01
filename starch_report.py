#!/usr/bin/env python
'''
Created on Oct 4, 2012

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import collections


import login
TROST_DB = login.get_db(db='trost_prod')
C = TROST_DB.cursor()

import water_content as WC

DROP_PHENO_DUMMY = """
DROP TABLE IF EXISTS pheno_dummy;
""".strip().replace('\n', ' ')

CREATE_PHENO_DUMMY = """
CREATE TABLE IF NOT EXISTS pheno_dummy (
id INT NOT NULL PRIMARY KEY, date DATE, plant_id INT
);
""".strip().replace('\n', ' ')

EMPTY_PHENO_DUMMY = """
DELETE FROM PHENO_DUMMY;
""".strip().replace('\n', ' ')

FILL_PHENO_DUMMY_1 = """ 
INSERT INTO pheno_dummy 
SELECT id, date, sample_id FROM phenotypes 
WHERE object = 'LIMS-Aliquot';
""".strip().replace('\n', ' ')

FILL_PHENO_DUMMY_2 = """ 
INSERT INTO pheno_dummy 
SELECT phenotypes.id, phenotypes.date, samples.plant_id FROM phenotypes, samples 
WHERE phenotypes.object = 'LIMS-Sample' AND
samples.id = phenotypes.sample_id;
""".strip().replace('\n', ' ')



FIELDS_188_190_191 = ['plant_id', 'subspecies', 'culture_id', 'value_id', 'number']
FIELDS_55_69 = ['plant_id', 'subspecies', 'culture_id',
                'p1_id', 'p1_date', 'p2_id', 'p2_date', 
                'value_id1', 'pv1_number', 'value_id2', 'pv2_number', 'entity']
FIELDS_163_164_69_225 = ['plant_id', 'subspecies', 'culture_id',
                         'p1_id', 'p1_date', 'p2_id', 'p2_date', 'p3_id', 'p3_date',   
                         'value_id1', 'pv1_number', 'value_id2', 'pv2_number', 
                         'value_id3', 'pv3_number', 
                         'entity']

HEADERS_188_190_191 = ['Culture_ID', 'Plant_ID', 'Subspecies', '188', '190', '191']
HEADERS_55_69_366 = []

# VALID_CULTURES = (44443, 45985, 45990, 46150, 48656, 56726, 56875, 57802, 57803, 58243, 60319)
VALID_CULTURES = (51790,)

QUERY_188_190_191 = """
SELECT 
%s
""".strip().replace('\n', ' ') % str(VALID_CULTURES)

QUERY_188_190_191 = """
SELECT
pheno_dummy.plant_id,
plants.name as subspecies,
cultures.id as culture_id,
phenotype_values.value_id as value_id, 
phenotype_values.number as number 
FROM pheno_dummy, phenotype_values, plants, cultures
WHERE
pheno_dummy.plant_id != 1 AND
phenotype_values.value_id IN (188, 190, 191) AND
pheno_dummy.id = phenotype_values.phenotype_id AND
plants.id = pheno_dummy.plant_id AND
cultures.id = plants.culture_id AND
cultures.id IN %s;
""".strip().replace('\n', ' ') % str(VALID_CULTURES)

QUERY_55_69_WRONG = """ 
SELECT
P1.plant_id,
plants.name AS subspecies,
plants.culture_id AS culture_id,
P1.id AS p1_id, P1.date AS p1_date, 
P2.id AS p2_id, P2.date AS p2_date, 
PV1.value_id AS value_id1, PV1.number AS pv1_number,
PV2.value_id AS value_id2, PV2.number AS pv2_number,
PE1.entity_id AS entity_id
FROM
plants,
pheno_dummy AS P1
LEFT JOIN pheno_dummy AS P2
ON P1.plant_id = P2.plant_id
LEFT JOIN phenotype_values AS PV1
ON P1.id = PV1.phenotype_id
LEFT JOIN phenotype_values AS PV2
ON P2.id = PV2.phenotype_id
LEFT JOIN phenotype_entities AS PE1
ON P1.id = PE1.phenotype_id
LEFT JOIN phenotype_entities AS PE2
ON P2.id = PE2.phenotype_id
WHERE 
plants.id = P1.plant_id AND
P1.id != P2.id AND 
(PV1.value_id = 55 AND PV2.value_id = 69) AND
(PE1.entity_id = %s AND PE1.entity_id = PE2.entity_id) AND
PV1.number IS NOT NULL AND PV2.number IS NOT NULL AND
culture_id IN %s
ORDER BY P1.plant_id, P1.date, P2.date;
""".strip().replace('\n', ' ') % ('%i', str(VALID_CULTURES))


QUERY_55_69 = """ 
SELECT
P1.plant_id,
plants.name AS subspecies,
plants.culture_id AS culture_id,
P1.id AS p1_id, P1.date AS p1_date, 
P2.id AS p2_id, P2.date AS p2_date,
P3.id AS p3_id, P3.date AS p3_date,  
PV1.value_id AS value_id1, PV1.number AS pv1_number,
PV2.value_id AS value_id2, PV2.number AS pv2_number,
PV3.value_id AS value_id3, PV3.number AS pv3_number,
PE1.entity_id AS entity_id1,
PE2.entity_id AS entity_id2,
PE3.entity_id AS entity_id3
FROM
plants,
pheno_dummy AS P1
LEFT JOIN pheno_dummy AS P2
ON P1.plant_id = P2.plant_id
LEFT JOIN pheno_dummy AS P3
ON P1.plant_id = P3.plant_id
LEFT JOIN phenotype_values AS PV1
ON P1.id = PV1.phenotype_id
LEFT JOIN phenotype_values AS PV2
ON P2.id = PV2.phenotype_id
LEFT JOIN phenotype_values AS PV3
ON P3.id = PV3.phenotype_id
LEFT JOIN phenotype_entities AS PE1
ON P1.id = PE1.phenotype_id
LEFT JOIN phenotype_entities AS PE2
ON P2.id = PE2.phenotype_id
LEFT JOIN phenotype_entities AS PE3
ON P3.id = PE3.phenotype_id
WHERE 
plants.id = P1.plant_id AND
P1.id != P2.id AND P1.id != P3.id AND P2.id != P3.id AND
(PV1.value_id = 55 AND PE1.entity_id = -12345) AND
(PV2.value_id = 69 AND PE2.entity_id = -12345) AND
(PV3.value_id = 55 AND PE3.entity_id = 12) AND
PV1.number IS NOT NULL AND PV2.number IS NOT NULL AND PV3.number IS NOT NULL AND
culture_id IN %s
ORDER BY P1.plant_id, P1.date, P2.date;
""".strip().replace('\n', ' ') % (str(VALID_CULTURES))


def compute_starch_from_fwdw(fw_dw):
    return (fw_dw * 100.0 - 6.0313) / 10.0

def prepare_data(C, query, fields):
    data = []
    C.execute(query)
    for row in C.fetchall():
        row_d = dict(zip(fields, row))
        data.append(row_d)
    return data

def process_data_188_190_191(data):
    data_d = collections.defaultdict(dict)
    for d in data:
        key = (d['culture_id'], d['plant_id'], d['subspecies'])
        data_d[key][d['value_id']] = d['number']
    return data_d 

def write_data(data, headers, write_headers=False, out=sys.stdout):
    if write_headers:
        out.write(','.join(map(str, headers)) + '\n')
    for k, v in sorted(data.items()):
        # print k, v 
        row = ('%i,%i,%s' % k).split(',')
        for head in headers[3:]:
            if head in v:
                row += [v[head]]
            else:
                row += ['']        
        
        # row += [v_[1] for v_ in sorted(v.items())]
        out.write(','.join(map(str, row)) + '\n')
        # break  
    pass  

ALL_HEADERS = ['Culture_ID', 'Plant_ID', 'Subspecies',
               55, 69, 188, 190, 191]

def process_data_55_69(data):
    data_d = collections.defaultdict(dict)
    for d in data:
        # print d
        key = (d['culture_id'], d['plant_id'], d['subspecies'])
        try:
            pv1_number = float(d['pv1_number'])
        except:
            continue
        try:
            pv2_number = float(d['pv2_number'])
        except:
            continue
        
        data_d[key][d['value_id1']] = pv1_number
        data_d[key][d['value_id2']] = pv2_number
        data_d[key]['pv1_number'] = pv1_number
        data_d[key]['pv2_number'] = pv2_number
        data_d[key]['p1_date'] = d['p1_date']
        data_d[key]['p2_date'] = d['p2_date']
        dw_fw, valid_row = WC.f_compute_DW_FW(data_d[key])
        data_d[key]['valid'] = valid_row
        
        fw = float(data_d[key]['pv1_number'])        
        dw = float(data_d[key]['pv2_number'])
        dw_fw = dw * 100.0 / fw
                
        data_d[key][190] = (dw_fw - 6.0313) / 10.0        
        data_d[key][191] = data_d[key][55] * data_d[key][190] / 1000.0
        # print data_d[key]
    return data_d




def main(argv):
    
    out = sys.stdout    
    
    # generate phenotypes with sample_ids mapped to plant_ids
    C.execute(DROP_PHENO_DUMMY)
    C.execute(CREATE_PHENO_DUMMY)
    # C.execute(EMPTY_PHENO_DUMMY)
    C.execute(FILL_PHENO_DUMMY_1)
    C.execute(FILL_PHENO_DUMMY_2)
    
    # get data from 188, 190, 191
    data = process_data_188_190_191(prepare_data(C, QUERY_188_190_191, FIELDS_188_190_191))
    write_data(data, out=out, headers=ALL_HEADERS, write_headers=True)
    
    # get data from -12345:55_69 (Pruef1.2?)
    # data = process_data_55_69(prepare_data(C, QUERY_55_69 % (-12345), FIELDS_55_69))
    # write_data(data, headers=ALL_HEADERS, out=out, write_headers=False)
    
    # C.execute(DROP_PHENO_DUMMY)
    pass

if __name__ == '__main__': main(sys.argv[1:])
