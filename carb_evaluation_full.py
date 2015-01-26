#!/usr/bin/env python
'''
Created on Jul 29, 2013

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
from collections import defaultdict

import numpy as np
import scipy.stats
import statsmodels.stats.multicomp as ssmc

from rp2 import robjects 
R = robjects.r

import login
TROST_DB = login.get_db(db='trost_prod')
C = TROST_DB.cursor()


# http://jamesjtripp.blogspot.de/2013/06/one-way-anova-statistics-in-python.html




CARB_QUERY = """
SELECT 
pl.culture_id AS culture,
pl.subspecies_id AS cultivar,
a.id AS aliquot, 
LOG(p1.number) AS C6,
LOG(p2.number) AS Glu,
LOG(p3.number) AS Fru,
LOG(p4.number) AS Sac,
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
GROUP BY a.id;
""".strip().replace('\n', ' ')

def compute_stats(data):
    mean = np.mean(data, dtype=np.float64)
    stdev = np.std(data, dtype=np.float64)
    return {'min': min(data),
            'max': max(data),
            'stdev': stdev,
            'median': np.median(data), 
            'mean': mean, 
            'cv': stdev / mean}

def write_data(data, out=sys.stdout):
    stats_order = ['min', 'max', 'mean', 'median', 'stdev', 'cv']    
    out.write(','.join(['carbohydrate', 'culture'] + stats_order) + '\n')
    
    for p_id, p_name in [(212, 'C6') , (131, 'Glucose'), (132, 'Fructose'), (142, 'Saccharose')]:
        out.write('%s (%i)\n' % (p_name, p_id))
        for trial in data:
            row = ['', str(trial)]
            stats = compute_stats(data[trial][p_id])
            out.write(','.join(row + ['%.5f' % stats[stat] for stat in stats_order]) + '\n')
    pass

def is_number(n):
    try:
        n = float(n)
    except:
        return False
    return True


def main(argv):
    
    trials = dict()    
    carbs = [212, 131, 132, 142]
    poolgroup_lut = {56575: 'a', 58243: 'a', 60319: 'a',
                     45990: 'b', 57803: 'b',
                     45985: 'c', 48656: 'c', 51790: 'c', 57802: 'c',
                     44443: 'd', 56726: 'd', 56875: 'd', 46150: 'd', 
                     47107: 'd', 47109: 'd', 47110: 'd', 47111: 'd', 
                     47112: 'd', 47114: 'd', 47115: 'd', 47117: 'd',
                     56876: 'd', 56877: 'd', 56878: 'd', 56879: 'd',
                     56880: 'd', 56881: 'd', 56882: 'd', 56883: 'd', 56884: 'd'}
    
    C.execute(CARB_QUERY) # yields: $culture, $subspecies, $aliquot, $c6_log, $glu_log, $fru_log, $sac_log, $treatment
    for row in C.fetchall():
        row = dict(zip(['cid', 'sid', 'pid'] + carbs + ['tid'], row))

        if int(row['cid']) not in trials:
            trials[int(row['cid'])] = {k: list() for k in carbs + ['tid', 'sid']}
        for k in trials[int(row['cid'])]:
            trials[int(row['cid'])][k].append(row[k])

    all_data = {k: list() for k in carbs}
    for k_trial in trials:
        for k_carb in carbs:
            all_data[k_carb].extend([float(x) for x in trials[k_trial][k_carb] if is_number(x)])

    for k in all_data: print k, len(all_data[k])
    all_stats = {k: compute_stats(all_data[k]) for k in all_data}
    print all_stats
    
    


    null_count = 0
    for k_carb in carbs:
        lb, ub = (all_stats[k_carb]['mean'] - 3 * all_stats[k_carb]['stdev'], all_stats[k_carb]['mean'] + 3 * all_stats[k_carb]['stdev'])
        for k_trial in trials:        
            for i, value in enumerate(trials[k_trial][k_carb]):
                if is_number(value) and (lb <= float(value) <= ub):
                    trials[k_trial][k_carb][i] = float(value)
                else:
                    trials[k_trial][k_carb][i] = None
                    null_count += 1
    print 'NULL:', null_count
    
    pooled = {k: {j: list() for j in 'abcd'} for k in carbs}
    for k in carbs:
        for t in trials:
            pooled[k][poolgroup_lut[t]].extend([v for v in trials[t][k] if not v is None])


                
        """
        from http://rpy.sourceforge.net/rpy2/doc-2.0/html/introduction.html#getting-started
        and http://rpy.sourceforge.net/rpy2/doc-2.1/html/robjects.html
        ctl = robjects.FloatVector([4.17,5.58,5.18,6.11,4.50,4.61,5.17,4.53,5.33,5.14])
        trt = robjects.FloatVector([4.81,4.17,4.41,3.59,5.87,3.83,6.03,4.89,4.32,4.69])
        group = r.gl(2, 10, 20, labels = ["Ctl","Trt"])
        weight = ctl + trt

        robjects.globalenv["weight"] = weight
        robjects.globalenv["group"] = group
        lm_D9 = r.lm("weight ~ group")
        print(r.anova(lm_D9))

        lm_D90 = r.lm("weight ~ group - 1")
        print(r.summary(lm_D90))
        
        print(lm_D9.rclass)
        print(lm_D9.names)
        lm_D9.rx2('coefficients')
        """
        
        """
        for j in 'abcd':
            pooled[k][j] = np.array(pooled[k][j])
        f_value, p_value = scipy.stats.f_oneway(pooled[k]['a'], pooled[k]['b'], pooled[k]['c'], pooled[k]['d'])
        data = np.hstack([pooled[k]['a'], pooled[k]['b'], pooled[k]['c'], pooled[k]['d']])
        labels = np.hstack([[j] * len(pooled[k][j]) for j in 'abcd'])
        result = ssmc.pairwise_tukeyhsd(data, labels)
        mod = ssmc.MultiComparison(data, labels)

        print 'Carb:', k
        print 'F = %.14e' % f_value, 'P = %.14e' % p_value
        print mod.tukeyhsd()
        """

        

        


    """
    trials['GolmFields'] = {key: trials[56726][key] + trials[44443][key] 
                            for key in (212, 131, 132, 142)}
    trials['AllFields'] = {key: trials[56726][key] + trials[44443][key] + trials[46150][key] + trials[56875][key] 
                           for key in (212, 131, 132, 142)}
    """    

    # write_data(trials, open('carbs_alltrials_log.csv', 'wb'))
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
