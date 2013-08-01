#!/usr/bin/env python
'''
Created on Oct 15, 2012

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys


def main(argv):
    pass

if __name__ == '__main__': main(sys.argv[1:])


QUERY_163_164_69_225 = """
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
PE1.entity_id AS entity_id
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
(PV1.value_id = 163 AND PV2.value_id = 164 AND (PV3.value_id = 69 OR PV3.value_id = 225)) AND
(PE1.entity_id IN (%s) AND PE1.entity_id = PE2.entity_id AND PE1.entity_id = PE3.entity_id) 
ORDER BY P1.plant_id, P1.date, P2.date, P3.date;
""".strip().replace('\n', ' ') % ('%i')#, str(VALID_CULTURES))

def process_data_163_164_69_225(data):
    data_d = collections.defaultdict(dict)
    for d in data:
        key = (d['culture_id'], d['plant_id'], d['subspecies'])
        data_d[key][d['value_id1']] = float(d['pv1_number'])
        data_d[key][d['value_id2']] = float(d['pv2_number'])
        data_d[key][d['value_id3']] = float(d['pv3_number'])
        data_d[key]['pv1_number'] = float(d['pv1_number'])
        data_d[key]['pv2_number'] = float(d['pv2_number'])
        data_d[key]['pv3_number'] = float(d['pv3_number'])
        data_d[key]['p1_date'] = d['p1_date']
        data_d[key]['p2_date'] = d['p2_date']
        data_d[key]['p3_date'] = d['p3_date']
        fw_dw, valid_row = WC.f_compute_FW_DW_V23(data_d[key])
        data_d[key]['valid'] = valid_row
        data_d[key][190] = compute_starch_from_fwdw(fw_dw)        
        data_d[key][191] = (data_d[key][164] - data_d[key][163]) * data_d[key][190] / 100.0
        # print data_d[key]    
    return data_d

# get data from 366:163,164,69/225 (field, leaf)
    # print QUERY_163_164_69_225 % 366
    # data = process_data_163_164_69_225(prepare_data(C, QUERY_163_164_69_225 % 366, FIELDS_163_164_69_225))
    # write_data(data, headers=ALL_HEADERS, out=out, write_headers=True)
