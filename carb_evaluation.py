#!/usr/bin/env python
'''
Created on Jul 29, 2013

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
from collections import defaultdict

import numpy
import scipy.stats

import login
TROST_DB = login.get_db(db='trost_prod')
C = TROST_DB.cursor()


CARB_QUERY = """
SELECT 
pl.culture_id AS culture,
pl.subspecies_id AS cultivar,
a.id AS aliquot, 
p1.number AS C6,
p2.number AS Glu,
p3.number AS Fru,
p4.number AS Sac,
p_treatment.value_id AS treatment
FROM
aliquots a
LEFT JOIN phenotype_aliquots AS pa1 ON a.id = pa1.aliquot_id
LEFT JOIN phenotypes p1 ON p1.id = pa1.phenotype_id
RIGHT JOIN phenotype_aliquots AS pa2 ON a.id = pa2.aliquot_id
RIGHT JOIN phenotypes p2 ON p2.id = pa2.phenotype_id
RIGHT JOIN phenotype_aliquots AS pa3 ON a.id = pa3.aliquot_id
RIGHT JOIN phenotypes p3 ON p3.id = pa3.phenotype_id
RIGHT JOIN phenotype_aliquots AS pa4 ON a.id = pa4.aliquot_id
RIGHT JOIN phenotypes p4 ON p4.id = pa4.phenotype_id
JOIN aliquot_plants AS ap ON ap.aliquot_id = a.id
JOIN plants AS pl ON pl.id = ap.plant_id
JOIN phenotype_plants AS pp ON pl.id = pp.plant_id
JOIN phenotypes AS p_treatment ON p_treatment.id = pp.phenotype_id
WHERE 
p1.value_id = 212 AND
p2.value_id = 131 AND
p3.value_id = 132 AND
p4.value_id = 142 AND
p_treatment.value_id IN (169,170,171,172)
GROUP BY a.id
LIMIT 0,10;
""".strip().replace('\n', ' ')



CARB_QUERY = """
SELECT 
pl.culture_id AS experiment,
pl.subspecies_id AS cultivar,
pa.aliquot_id, 
p.value_id, 
p.number,
p_treatment.value_id AS treatment
FROM
phenotypes p 
JOIN phenotype_aliquots AS pa ON p.id=pa.phenotype_id 
JOIN aliquot_plants AS ap ON ap.aliquot_id = pa.aliquot_id 
JOIN plants AS pl ON pl.id = ap.plant_id
JOIN phenotype_plants AS pp ON pl.id = pp.plant_id
JOIN phenotypes AS p_treatment ON p_treatment.id = pp.phenotype_id
WHERE 
p.value_id IN (212,131,132,142) AND
p_treatment.value_id IN (169,170,171,172)
GROUP BY pa.aliquot_id,p.value_id
LIMIT 0,10;
""".strip().replace('\n', ' ')




CARB_QUERY = """
SELECT 
pl.culture_id, 
pa.aliquot_id, 
p.value_id, 
p.number 
FROM
phenotypes p 
JOIN phenotype_aliquots AS pa ON p.id=pa.phenotype_id 
JOIN aliquot_plants AS ap ON ap.aliquot_id = pa.aliquot_id 
JOIN plants AS pl ON pl.id = ap.plant_id 
WHERE 
p.value_id IN (212,131,132,142) 
GROUP BY pa.aliquot_id,p.value_id;
""".strip().replace('\n', ' ')

def compute_stats(data):
    mean = numpy.mean(data, dtype=numpy.float64)
    stdev = numpy.std(data, dtype=numpy.float64)
    return {'min': min(data),
            'max': max(data),
            'stdev': stdev,
            'median': numpy.median(data), 
            'mean': mean, 
            'cv': stdev / mean}


def write_data(data, out=sys.stdout):
    stats_order = ['min', 'max', 'mean', 'median', 'stdev', 'cv']    
    # out.write(','.join(['culture', 'carb'] + stats_order) + '\n')
    out.write(','.join(['carbohydrate', 'culture'] + stats_order) + '\n')
    
    for p_id, p_name in [(212, 'C6') , (131, 'Glucose'), (132, 'Fructose'), (142, 'Saccharose')]:
        out.write('%s (%i)\n' % (p_name, p_id))
        for trial in data:
            row = ['', str(trial)]
            stats = compute_stats(data[trial][p_id])
            out.write(','.join(row + ['%.5f' % stats[stat] for stat in stats_order]) + '\n')
        
    """
    for trial in data:
        # print trial
        for param in data[trial]:
            row = map(str, [trial, param])
            stats = compute_stats(data[trial][param])
            out.write(','.join(row + ['%.5f' % stats[stat] for stat in stats_order]) + '\n')
    """
    pass
            
            
            
    


def main(argv):
    
    trials = dict()    
    # {212: [], 131: [], 132: [], 142: []}
    #(56575L, 1378949L, 142L, '12.2805116045')

    C.execute(CARB_QUERY)
    for row in C.fetchall():
        # print row
        try:
            trials[int(row[0])][int(row[2])].append(float(row[3]))
        except:
            trials[int(row[0])] = {212: list(), 131: list(), 132: list(), 142: list()}
            trials[int(row[0])][int(row[2])].append(float(row[3])) 
    # print trials.keys()
    trials['GolmFields'] = {key: trials[56726][key] + trials[44443][key] 
                            for key in (212, 131, 132, 142)}
    trials['AllFields'] = {key: trials[56726][key] + trials[44443][key] + trials[46150][key] + trials[56875][key] 
                           for key in (212, 131, 132, 142)}
    
    logtrials = {}
    for trial in trials:
        logtrials[trial] = {param: numpy.log(trials[trial][param]) for param in trials[trial]}    
    
    write_data(trials, open('carbs_alltrials.csv', 'wb'))
    write_data(logtrials, open('carbs_alltrials_log.csv', 'wb'))
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
