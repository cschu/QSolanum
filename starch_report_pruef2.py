#!/usr/bin/env python
'''
Created on Oct 12, 2012

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys

import sys
import collections

import login

from starch_report import prepare_data



PRUEF12_QUERY = """
SELECT phenotypes.id, 
phenotype_entities.entity_id, 
phenotype_values.value_id,
phenotype_values.number,
plants.id as plant_id, 
plants.name, 
plants.subspecies_id, 
plants.culture_id
FROM pheno_dummy, phenotypes, phenotype_entities, phenotype_values, plants
WHERE
pheno_dummy.plant_id = plants.id AND pheno_dummy.id = phenotypes.id AND
phenotype_values.phenotype_id = phenotypes.id AND
phenotype_entities.phenotype_id = phenotypes.id AND
plants.culture_id = 48656 AND
phenotype_entities.entity_id IN (12, 808, -12345) AND
phenotype_values.value_id IN (55, 69) AND
phenotype_values.number IS NOT NULL;
""".strip().replace('\n', ' ')


PRUEF2_QUERY = """
SELECT 
P.id, P.entity_id, P.value_id, P.number, 
PL.id as plant_id, PL.name, PL.subspecies_id, 
C.id as culture_id 
FROM phenotypes P, phenotype_plants PP, plants PL, cultures C 
WHERE P.id = PP.phenotype_id AND 
PL.id = PP.plant_id AND 
C.id = PL.culture_id AND 
C.id IN (48656, 56575, 58243) AND 
P.entity_id IN (12, 810) AND 
P.value_id IN (55,69) AND 
P.number IS NOT NULL;
""".strip().replace('\n', ' ')

TROSTTEST2_QUERY = """
SELECT 
P.id, P.entity_id, P.value_id, P.number, 
PL.id as plant_id, PL.name, PL.subspecies_id, 
C.id as culture_id 
FROM phenotypes P, phenotype_plants PP, plants PL, cultures C 
WHERE P.id = PP.phenotype_id AND 
PL.id = PP.plant_id AND 
C.id = PL.culture_id AND 
C.id = 51790 AND 
P.entity_id IN (12, 810) AND 
P.value_id IN (55,69) AND 
P.number IS NOT NULL;
""".strip().replace('\n', ' ')

"""
SELECT P.id, P.entity_id, P.value_id, P.number, PL.id as plant_id, PL.name, PL.subspecies_id, C.id as culture_id FROM phenotypes P, phenotype_plants PP, plants PL, cultures C WHERE P.id = PP.phenotype_id AND PL.id = PP.plant_id AND C.id = PL.culture_id AND C.id IN (48656, 58243) AND P.value_id IN (55,69) AND P.number IS NOT NULL;
"""



PRUEF2_FIELDS = ['id', 'entity_id', 'value_id', 'number', 'plant_id', 'name', 'subspecies_id', 'culture_id']
 

target = "Culture_ID    Plant_ID    Subspecies    55    69    163    164    188    225    190    191"

"""Staerkeformel nach Methodenvorschrift Bundessortenamt:
A = Staerkegehalt (%) =(0,0517 * UWG bei 5050g) - 5,2463
B = Trockenmassegehalt (%) =(0,052 * UWG bei 5050g) + 0,785

=> 

A = 0.0517 [ (B - 0.785) / 0.052 ] - 5.2463
A = 0.9942B - 6.0268
"""


def compute_starch(row):
    
    # print row
    
    if not (810, 69) in row:
        return None
    if not (12, 55) in row:
        return None
    if not (810, 55) in row:
        return None
    try:
        FW = float(row[(810, 55)])
    except:
        return None  
    try:
        DW = float(row[(810, 69)])
    except:
        return None
    
    try:
        tuber_mass = float(row[(12, 55)])
    except:
        return None    
    drymass = DW/FW * 100.0
    
    
    starch_content = (drymass - 6.0313) * 10.0
    starch_yield = starch_content * tuber_mass / 1000.0
    return starch_content, starch_yield 

def process_data(data):
    plant_d = collections.defaultdict(dict)
    for d in data:
        entity = d['entity_id']
        if entity == -12345 or entity < 0:
            entity = 808
        key = (entity, d['value_id'])
        plant_id = d['plant_id']
        plant_d[plant_id][key] = d['number']
        plant_d[plant_id]['name'] = d['name']
        plant_d[plant_id]['subspecies_id'] = d['subspecies_id']
        plant_d[plant_id]['culture_id'] = d['culture_id']
    for k, v in sorted(plant_d.items()):
        starch = compute_starch(v)
        if starch is not None:
            row = [v['culture_id'], k, v['name'], 
                   v[(12, 55)], '', v[(810, 55)], v[(810, 69)], '', starch[0], starch[1]]
            print ','.join(map(str, row))
    pass
    

def main(argv):


    
    print ','.join(['Culture_ID', 'Plant_ID', 'Subspecies', '55_12', 
                    '69_12', '55_810', '69_810', '188', '190', '191'])
    
    # TROST_DB = login.get_db(db='trost_prod')
    # C = TROST_DB.cursor()
    # process_data(prepare_data(C, PRUEF12_QUERY, PRUEF2_FIELDS))
    TROST_DB = login.get_db()
    C = TROST_DB.cursor()
    # process_data(prepare_data(C, PRUEF2_QUERY, PRUEF2_FIELDS))
    process_data(prepare_data(C, TROSTTEST2_QUERY, PRUEF2_FIELDS))
    
    
    
    
    
    
         
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
