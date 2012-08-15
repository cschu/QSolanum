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

FIELDS = ['sample_id', 'p1_id', 'p1_date', 
          'pv1_id', 'pv1_value_id', 'pv1_phenotype_id', 'pv1_number', 'pe1_entity_id',
          'p2_id', 'p2_date',
          'pv2_id', 'pv2_value_id', 'pv2_phenotype_id', 'pv2_number', 'pe2_entity_id']

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


WC_TRIPLES_QUERY = """ 
select 
P1.sample_id as sample_id, 
P1.id as p1_id, P1.date as p1_date, 
PV1.*,
P2.id as p2_id, P2.date as p2_date,
PV2.*,
P3.id as p3_id, P3.date as p3_date,
PV3.*,
PE1.entity_id as entity_id

from 
phenotypes as P1 
left join phenotypes as P2
on P1.sample_id = P2.sample_id

left join phenotypes as P3
on P1.sample_id = P3.sample_id

left join phenotype_values as PV1
on P1.id = PV1.phenotype_id

left join phenotype_values as PV2
on P2.id = PV2.phenotype_id

left join phenotype_values as PV3
on P3.id = PV3.phenotype_id

left join phenotype_entities as PE1
on P1.id = PE1.phenotype_id

left join phenotype_entities as PE2
on P2.id = PE2.phenotype_id

left join phenotype_entities as PE3
on P3.id = PE3.phenotype_id

where 
P1.id != P2.id and P1.id != P3.id and P2.id != P3.id and
P1.object = 'LIMS-Aliquot' and P2.object = 'LIMS-Aliquot' and P3.object = 'LIMS-Aliquot' and
((PV1.value_id = 55 and PV2.value_id = 156 and PV3.value_id = 69) or 
(PV1.value_id = 163 and PV2.value_id = 164 and (PV3.value_id = 69 or PV3.value_id = 225))) and
(PE1.entity_id in (12,366) and PE1.entity_id = PE2.entity_id and PE1.entity_id = PE3.entity_id)
ORDER BY sample_id, P1.date, P2.date, P3.date;
""".strip().replace('\n', ' ')


WC_FWDW_V1_QUERY = """
select 
P1.sample_id as sample_id, 
P1.id as p1_id, P1.date as p1_date, 
PV1.*,
P2.id as p2_id, P2.date as p2_date,
PV2.*,
PE1.entity_id as entity_id

from 
phenotypes as P1 
left join phenotypes as P2
on P1.sample_id = P2.sample_id

left join phenotype_values as PV1
on P1.id = PV1.phenotype_id

left join phenotype_values as PV2
on P2.id = PV2.phenotype_id

left join phenotype_entities as PE1
on P1.id = PE1.phenotype_id

left join phenotype_entities as PE2
on P2.id = PE2.phenotype_id

where 
P1.id != P2.id and 
P1.object = 'LIMS-Aliquot' and P2.object = 'LIMS-Aliquot' and 
(PV1.value_id = 55 and PV2.value_id = 69) and
(PE1.entity_id = 366 and PE1.entity_id = PE2.entity_id) 
ORDER BY sample_id, P1.date, P2.date;
""".strip().replace('\n', ' ')

WC_FWDW_V1_FIELDS = ['sample_id',
                     'p1_id', 'p1_date', 
                     'pv1_id', 'pv1_value_id', 'pv1_phenotype_id', 'pv1_number',
                     'p2_id', 'p2_date', 
                     'pv2_id', 'pv2_value_id', 'pv2_phenotype_id', 'pv2_number',
                     'entity_id']

WC_TRIPLES_FIELDS = ['sample_id',
                     'p1_id', 'p1_date', 
                     'pv1_id', 'pv1_value_id', 'pv1_phenotype_id', 'pv1_number',
                     'p2_id', 'p2_date', 
                     'pv2_id', 'pv2_value_id', 'pv2_phenotype_id', 'pv2_number',
                     'p3_id', 'p3_date', 
                     'pv3_id', 'pv3_value_id', 'pv3_phenotype_id', 'pv3_number',
                     'entity_id']

def check_date(date1, date2, date_range):
    delta_t = date2 - date1    
    return delta_t >= datetime.timedelta(days=date_range[0]) and \
        delta_t <= datetime.timedelta(days=date_range[1])     

def make_bitflags(values):
    return reduce(lambda x,y:x|y, [int(x)<<i 
                                   for i, x in enumerate(values)])
    
def make_row_string(row_d, fields, sep=';'):
    return sep.join([str(row_d[field]) for field in fields])

def compute_stuff(data, fields, out, label, f_check_and_compute):
    out.write('%s\n' % (';'.join(fields + ['is_valid', 'value'])))
    results = []
    for row_d in data:
        print row_d
        row_value, valid_row = f_check_and_compute(row_d)
        row_string = make_row_string(row_d, fields)
        out.write('%s\n' % (row_string + ';%s;%.5f' % (str(valid_row), row_value)))
        
        results.append((row_d['sample_id'], (label, row_value, valid_row)))
        pass
    out.close()
    return results

def f_compute_RWC(row_d):
    valid_date = check_date(row_d['p1_date'], row_d['p2_date'], (1, 2))
    valid_date &= check_date(row_d['p1_date'], row_d['p3_date'], (2, 7))
    fw = float(row_d['pv1_number'])
    sw = float(row_d['pv2_number'])
    dw = float(row_d['pv3_number'])
    valid_values = (sw >= fw >= dw)
    rwc = (fw - dw) / (sw - dw)
    valid_result = (0.0 <= rwc <= 1.0)
    valid_row = make_bitflags([valid_date, valid_values, valid_result])    
    return rwc, valid_row

def f_compute_FW_DW_V1(row_d):
    valid_date = check_date(row_d['p1_date'], row_d['p2_date'], (1, 7))
    fw = float(row_d['pv1_number'])
    dw = float(row_d['pv2_number'])
    valid_values = (fw >= dw)
    fw_dw = fw / dw
    valid_result = (1.0 <= fw_dw <= 15.0)
    valid_row = make_bitflags([valid_date, valid_values, valid_result])
    return fw_dw, valid_row
    
def f_compute_FW_DW_V23(row_d):
    valid_date = check_date(row_d['p2_date'], row_d['p1_date'], (-10, -1))
    valid_date &= check_date(row_d['p2_date'], row_d['p3_date'], (1, 7))
    tara = float(row_d['pv1_number'])
    fwb = float(row_d['pv2_number'])
    dw = float(row_d['pv3_number'])
    valid_values = (fwb >= tara)
    
    if row_d['pv3_value_id'] == 69:
        fw_dw = (fwb - tara) / dw
    elif row_d['pv3_value_id'] == 225:
        fw_dw = (fwb - tara) / (dw - tara)
    else:
        fw_dw = -1.0
    valid_result = (1.0 <= fw_dw <= 15.0)
    valid_row = make_bitflags([valid_date, valid_values, valid_result])    
    return fw_dw, valid_row
    
#
def prepare_data(C, query, fields):
    data = []
    C.execute(query)
    for row in C.fetchall():
        row_d = dict(zip(fields, row))
        data.append(row_d)
    return data

def main(argv):
    #fw_dw_v1 = (prepare_data(C, WC_FWDW_V1_QUERY, WC_FWDW_V1_FIELDS))
    fw_dw_v1 = compute_stuff(prepare_data(C, WC_FWDW_V1_QUERY, WC_FWDW_V1_FIELDS),
                             WC_FWDW_V1_FIELDS,
                             open('fwdw_v1_data.csv', 'w'),
                             'fwdw_v1',
                             f_compute_FW_DW_V1)
    
    triple_data = prepare_data(C, WC_TRIPLES_QUERY, WC_TRIPLES_FIELDS)
    rwc_data = [row_d for row_d in triple_data if row_d['pv1_value_id'] == 55]
    fw_dw_v23_data = [row_d for row_d in triple_data if row_d['pv1_value_id'] == 163]
    
    rwc = compute_stuff(rwc_data,
                        WC_TRIPLES_FIELDS,
                        open('rwc_data.csv', 'w'),
                        'rwc',
                        f_compute_RWC)
    fw_dw_v23 = compute_stuff(fw_dw_v23_data, 
                              WC_TRIPLES_FIELDS,
                              open('fwdw_v23_data.csv', 'w'), 
                              'fwdw_v23', 
                              f_compute_FW_DW_V23)
    
    all_items = fw_dw_v1 + fw_dw_v23 + rwc
    all_d = {}
    for key, val in all_items:
        # print key, val
        if val[2] == 7:
            all_d[key] = all_d.get(key, []) + [val[:2]] #[(v[:2]) for v in val if v[2] == 7]
        
    fo = open('wc_results.csv', 'w')
    headers = ['Aliquot|Sample_ID', 'fw_dw1', 'fw_dw2', 'rwc1', 'rwc2']
    fo.write('%s\n' % (','.join(headers)))
    
    for key, val in sorted(all_d.items()):
        print key, val
        fwdw_count = 0
        row = ['%i' % key]
        for v in val:
            if v[0].startswith('fwdw'):
                fwdw_count += 1
                row.append('%.5f' % v[1])
            elif v[0] == 'rwc' and fwdw_count < 2:
                row.append('N/A')
                fwdw_count += 1
                row.append('%.5f' % v[1])
            else:
                row.append('%.5f' % v[1])
        if len(row) < 5:
            row.append('N/A')
        fo.write('%s\n' % (','.join(row)))
    
    
    fo.close()
            
        
    
    
    
    pass
    

def main2(argv):
    
    C.execute(WATER_CONTENTS_QUERY)
    
    fo = open('water_contents.csv', 'w')
    fo.write('%s\n' % (';'.join(FIELDS)))
    data = {}
    for row in C.fetchall():
        fo.write('%s\n' % (';'.join(map(str, row))))
        row_d = dict(zip(FIELDS, row))
        data[row_d['sample_id']] = data.get(row_d['sample_id'], []) + [row_d]
    fo.close()
        
    for key in data:
        
        if len(data[key]) == 1:
            del data[key]
        else:
            # print 'ANNOY!'
            compute_stuff(data[key])
        pass      

        
        
        
    
    # print data[0]
    
    #data_d = {}
    #for 
    #print data.items()[:4]
    #for item in data.items():
    #    if len(item[1]) > 1:
    #        print item

    
        
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


#def compute_rwc(data):
#    candidate_69 = None
#    candidate_156 = None
#    for row in sorted(data, key=lambda x:x['delta_t']):
#        # print row
#        if row['pv2_value_id'] == 69 and row['delta_t'] >= datetime.timedelta(days=2) and row['delta_t'] <= datetime.timedelta(days=7):
#            if candidate_69 is None:
#                candidate_69 = row
#            else:
#                print 'Duplicate value (69):'
#                print 'Original:', candidate_69
#                print 'Duplicate:', row
#        elif row['pv2_value_id'] == 156 and row['delta_t'] >= datetime.timedelta(days=1) and row['delta_t'] <= datetime.timedelta(days=2):
#            if candidate_156 is None:
#                candidate_156 = row
#            else:
#                print 'Duplicate value (156):'
#                print 'Original:', candidate_156
#                print 'Duplicate:', row
#        pass
#    # if not candidate_69 is None and not candidate_156 is None:
#    #    print 'CANDIDATES:', candidate_69, candidate_156
#    """
#    if len(candidates_69) > 1:
#        print 'Duplicate 69', 
#        candidates_69 = sorted(candidates_69, key=lambda x:x['delta_t'])
#    if len(candidates_156) > 1:
#        candidates_156 = sorted(candidates_156, key=lambda x:x['delta_t'])
#    """
#    return None
#
#def compute_stuff(data):
#    #delta_t = []     
#    for i, row in enumerate(data):         
#        data[i]['delta_t'] = row['p2_date'] - row['p1_date']
#    data_55 = [row for row in data if row['pv1_value_id'] == 55 and row['delta_t'] > datetime.timedelta(days=0)]
#    # print data_55
#    compute_rwc(data_55)
#    
#    pass            


#def main(argv):
#    
#    C.execute(WATER_CONTENTS_QUERY)
#    
#    fo = open('water_contents.csv', 'w')
#    fo.write('%s\n' % (';'.join(FIELDS)))
#    data = {}
#    for row in C.fetchall():
#        fo.write('%s\n' % (';'.join(map(str, row))))
#        row_d = dict(zip(FIELDS, row))
#        data[row_d['sample_id']] = data.get(row_d['sample_id'], []) + [row_d]
#    fo.close()
#        
#    for key in data:
#        
#        if len(data[key]) == 1:
#            del data[key]
#        else:
#            # print 'ANNOY!'
#            compute_stuff(data[key])
#        pass      
#
#        
#        
#        
#    
#    # print data[0]
#    
#    #data_d = {}
#    #for 
#    #print data.items()[:4]
#    #for item in data.items():
#    #    if len(item[1]) > 1:
#    #        print item
#
#    
#        
#    """
#    fw_data = [row for row in data if row['value_id'] == 55]
#    sw_data = [row for row in data if row['value_id'] == 156]
#    dw_data = [row for row in data if row['value_id'] == 69]
#    tara_data = [row for row in data if row['value_id'] == 163]
#    fwb_data = [row for row in data if row['value_id'] == 164]
#    
#    sw_data = sorted(sw_data, key=lambda x:(x['sample_id'], x['date'], x['time']))
#    print sw_data[:4]
#    print len(data), len(fw_data) + len(sw_data) + len(dw_data) + len(tara_data) + len(fwb_data)
#    """
#    
#    
#    # print C.fetchall()
#    
#    
#    
#    
#    
#    TROST_DB.close()
#    pass


##
#def compute_RWC(data, fields=WC_TRIPLES_FIELDS):
#    out = open('rwc_data.csv', 'w')
#    out.write('%s\n' % (';'.join(fields + ['is_valid', 'value'])))
#    results = []
#    for row_d in data:
#        print row_d
#        valid_date = check_date(row_d['p1_date'], row_d['p2_date'], (1, 2))
#        valid_date |= check_date(row_d['p1_date'], row_d['p3_date'], (2, 7))
#        fw = float(row_d['pv1_number'])
#        sw = float(row_d['pv2_number'])
#        dw = float(row_d['pv3_number'])
#        valid_values = (sw >= fw >= dw)
#        rwc = (fw - dw) / (sw - dw)
#        valid_result = (0.0 <= rwc <= 1.0)
#        valid_row = make_bitflags([valid_date, valid_values, valid_result])    
#        row_string = make_row_string(row_d, fields) 
#        out.write('%s\n' % (row_string + ';%s;%.5f' % (str(valid_row), rwc)))
#        
#        results.append((row_d['sample_id'], ('RWC', rwc, valid_row)))
#        pass
#    out.close()
#    return results

##
#def compute_FW_DW_V1(data, fields=WC_FWDW_V1_FIELDS):
#    out = open('fwdw_v1_data.csv', 'w')
#    out.write('%s\n' % (';'.join(fields + ['is_valid', 'value'])))
#    results = []     
#    for row_d in data:        
#        print row_d
#        valid_date = check_date(row_d['p1_date'], row_d['p2_date'], (1, 7))
#        fw = float(row_d['pv1_number'])
#        dw = float(row_d['pv2_number'])
#        valid_values = (fw >= dw)
#        fw_dw = fw / dw
#        valid_result = (1.0 <= fw_dw <= 15.0)
#        valid_row = make_bitflags([valid_date, valid_values, valid_result])
#        row_string = make_row_string(row_d, fields) 
#        out.write('%s\n' % (row_string + ';%s;%.5f' % (str(valid_row), fw_dw)))
#        
#        results.append((row_d['sample_id'], ('FW_DW_V1', fw_dw, valid_row)))        
#        pass
#    out.close()
#    return results

if __name__ == '__main__': main(sys.argv[1:])
