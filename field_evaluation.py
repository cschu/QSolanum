#!/usr/bin/env python
'''
Created on May 28, 2013

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys

import numpy
import scipy.stats

import login
TROST_DB = login.get_db(db='trost_prod')
C = TROST_DB.cursor()

# +-----+-----------------------+-------+
#| id  | attribute             | value |
#+-----+-----------------------+-------+
#| 188 | absolute fresh weight | kg    |
#| 190 | Staerkegehalt         | g/kg  |
#| 191 | Staerkeertrag         | kg    |
#+-----+-----------------------+-------+

#
BREEDER_LOCATIONS = (5519, 5539, 5540, 5541, 5542, 5543, 5544, 5545, 5546)
#
TRIALS_2011 = (46150, 47107, 47109, 47110, 47111, 47112, 47114, 47115, 47117) 
#
TRIALS_2012 = (56876, 56877, 56878, 56879, 56880, 56881, 56882, 56883, 56884)

TRIAL_D = {'TRIALS_2011': (47107, 47109, 47110, 47111, 47112, 47114, 47115, 47117),
           'TRIALS_2012': (56876, 56877, 56878, 56879, 56880, 56881, 56882, 56883, 56884)}

SUBSPECIES_QUERY = """
SELECT id FROM subspecies WHERE id NOT IN (1, 91) AND id > 0
""".strip().replace('\n', ' ')

STARCH_QUERY = """ 
SELECT 
PL.id, 
PL.culture_id, 
PL.subspecies_id, 
p1.number AS FW_abs, 
p2.number AS starch_content, 
p3.number AS starch_yield,
C.pflanzabstand as dist_plants,
C.reihenabstand as dist_rows,
C.plantspparcelle as n_plants,
C.location_id as location,
p4.value_id as `condition`
FROM 
plants PL 
JOIN phenotype_plants AS pp1 ON pp1.plant_id = PL.id 
JOIN phenotypes as p1 ON p1.id = pp1.phenotype_id 
JOIN phenotype_plants AS pp2 ON pp2.plant_id = PL.id 
JOIN phenotypes as p2 ON p2.id = pp2.phenotype_id 
JOIN phenotype_plants AS pp3 ON pp3.plant_id = PL.id 
JOIN phenotypes as p3 ON p3.id = pp3.phenotype_id
JOIN phenotype_plants as pp4 ON pp4.plant_id = PL.id
JOIN phenotypes as p4 ON p4.id = pp4.phenotype_id
JOIN cultures as C ON PL.culture_id = C.id
WHERE
p1.value_id = 188 AND
p2.value_id = 190 AND
p3.value_id = 191 AND
p4.value_id IN (169, 170, 171) AND
PL.culture_id IN %s
""".strip().replace('\n', ' ')

STARCH_QUERY_2012 = STARCH_QUERY % str(TRIALS_2012)
STARCH_QUERY_2011 = STARCH_QUERY % str(TRIALS_2011)

STARCH_QUERY_FIELDS = ['plantID', 'cultureID', 'subspeciesID', 'tuberMass', 'starchContent', 'starchYield', 'dist_plants', 'dist_rows', 'n_plants', 'location', 'condition']
STARCH_QUERY_CASTS = [int, int, int, float, float, float, float, float, int, int, int]

def checkStarchContent(obj):
    starchContent = getattr(obj, 'starchContent')
    test = (100 <= starchContent <= 300)
    if starchContent < 100:
        # hax : in 2012 only one entry is < 100, it's probably a typo
        # in 2011, there are multiple sites with starchContent being 
        # given in [%] instead of [g/kg].
        # The singleton in 2012 made the issue impossible to spot and
        # lead to wrong starch yield calculations. Hence, the starch
        # content adjustment needs to be followed up by re-calculation
        # of the yield-parameters (=> patchStarchContent())
        # was: setattr(obj, 'starchContent', starchContent * 10.0)
        obj.patchStarchContent()
        test = True
    
    if not test:
        obj.isSane = False
        sys.stderr.write('FAILED: %s - starchContent (%s) out of bounds.\n' % (obj, obj.starchContent))
    return test


class StarchData(object):
    def __init__(self, **kwargs):
        self.keys = kwargs.keys()
        self.isSane = True
        
        for k in kwargs:
            setattr(self, k, kwargs[k])
            
        try:
            self.starchYieldPlant = self.calculateStarch_abs()
        except:
            print 'WEIRDNESS_1', self
        try:
            self.yieldPerHectar = self.calculate_yield_per_ha()
        except:
            print 'WEIRDNESS_2', self
            pass        
        pass        
    def __str__(self):
        return ';'.join(['%s=%s' % (k, getattr(self, k)) for k in self.keys])
    def __repr__(self):
        return str(self)
    def check_sanity(self, checks=[]):
        sanity = True
        for check_f in checks:
            sanity &= check_f(self)                
        return sanity
    def calculate_yield_per_ha(self):
        """
        Calculates starch yield [kg=1k g]/ area [ha=10k sqm]
        X = starchYieldPlant [g/plant]
        Y = plants_m2 [plants/sqm]
        yield_per_ha [kg/ha] = X/1000 * Y * 10000 = X * Y * 10  
        """
        plants_m2 = 10000.0 / (self.dist_plants * self.dist_rows)        
        return self.starchYieldPlant * plants_m2 * 10.0
    def calculateStarch_abs(self):
        """ Calculates starch yield / plant """
        return self.starchContent * self.tuberMass / float(self.n_plants)
    def key(self):
        return self.subspeciesID, self.plantID
    def patchStarchContent(self, factor=10.0):
        try:
            self.starchContent *= factor
        except:
            print 'WEIRDNESS: NO STARCH CONTENT!'
            print self
            sys.exit()
        self.starchYieldPlant = self.calculateStarch_abs()
        self.yieldPerHectar = self.calculate_yield_per_ha()
        pass
    
    pass


def prepare_data(C, query, fields, casts):
    data = []
    C.execute(query)
    
    for row in C.fetchall():
        try:
            row_d = dict(zip(fields, 
                             [cast(value) for cast, value in zip(casts, row)]))
            data.append(StarchData(**row_d))
        except:
            print 'ERR', row
            continue
    location = data[0].location
    return data, location

def compute_stats(data):
    mean = numpy.mean(data, dtype=numpy.float64)
    return {'median': numpy.median(data), 
            'mean': mean, 
            'cv': numpy.std(data, dtype=numpy.float64) / mean}

def do_compute(paramlist, source, results):
    for param in paramlist:
        values = [getattr(d, param) for d in source]
        results[param] = compute_stats(values)
    pass


def compute_devMedianPlant():
    pass


def main(argv):
    trial_year = argv[0]
    PARAM_LIST = ['starchContent', 'tuberMass', 'starchYieldPlant', 'yieldPerHectar']
    
    trial_data = {}
    trial_params = {trial: {} for trial in TRIAL_D[trial_year]}    
    alltrials_params = {param: [] for param in PARAM_LIST}
    alltrials_data = []
    
    C.execute(SUBSPECIES_QUERY)    
    subspecies_params = {key: {} for key in [int(row[0]) for row in C.fetchall()]}
    subspecies_data = {key: {} for key in subspecies_params}
    subspecies_means = {key: {param: [] for param in PARAM_LIST} for key in subspecies_params}
    subspecies_medians = {key: {param: [] for param in PARAM_LIST} for key in subspecies_params}
    
    fieldstats_out = open('field_statistics_%s.csv' % trial_year.strip('TRIALS_'), 'wb')
    fieldstats_header = ['CultureID', 
                         'Location',
                         '#Parzellen',
                         'Pflanzen/Parzelle', 
                         'mean_Knollenmasse_kgFW',
                         'median_Knollenmasse_kgFW',
                         'cv_Knollenmasse_kgFW',
                         'mean_Staerkegehalt_g/kg',
                         'median_Staerkegehalt_g/kg',
                         'cv_Staerkegehalt_g/kg',
                         'mean_Staerkeertrag_g/plant',
                         'median_Staerkeertrag_g/plant',
                         'cv_Staerkeertrag_g/plant',
                         'mean_Staerkeertrag_kg/ha',
                         'median_Staerkeertrag_kg/ha',
                         'cv_Staerkeertrag_kg/ha']
                         
    fieldstats_out.write(','.join(fieldstats_header) + '\n')
    param_order = ['tuberMass', 'starchContent', 'starchYieldPlant', 'relYieldPlant', 'yieldPerHectar']
    stats_order = ['mean', 'median', 'cv']
    
    fieldcult_out = open('field_cultivars_%s.csv' % trial_year.strip('TRIALS_'), 'wb')
    # fieldcult_header = ['Cultivar'] + ['%s_%s' % (fh, cid) for cid in TRIALS_2012 for fh in fieldstats_header[3:]]
    fieldcult_header = ['Cultivar', 'Culture', 'Location'] + [fh for fh in fieldstats_header[3:]]
    fieldcult_header += ['Dev_Staerkeertrag_median_plant', 'Dev_Staerkeertrag_median_ha']
    fieldcult_out.write(','.join(fieldcult_header) + '\n')
    rel_headers = ['mean_StaerkeertragRel',
                   'median_StaerkeertragRel',
                   'cv_StaerkeertragRel']
    
    globalcult_out = open('global_cultivars_%s.csv' % trial_year.strip('TRIALS_'), 'wb')
    globalcult_header = ['Cultivar'] + fieldstats_header[4:-3] + rel_headers + fieldstats_header[-3:] 
    globalcult_out.write(','.join(globalcult_header) + '\n')    
    
    
    
    for trial in TRIAL_D[trial_year]:
        row_data = [str(trial)]
        # print 'TRIAL:', trial
        # STARCH_QUERY % str(TRIALS_2012)
        #the_starch_query = STARCH_QUERY % str(TRIAL_D[trial_year])
        trial_data[trial], location = prepare_data(C, STARCH_QUERY % '(%s)' % trial, STARCH_QUERY_FIELDS, STARCH_QUERY_CASTS)
        # print 'Data size:', len(trial_data[trial])
        row_data.append(str(location))
        row_data.append(str(len(trial_data[trial])))
        row_data.append(str(trial_data[trial][0].n_plants))
        
        alltrials_data.extend(trial_data[trial])
        if len(trial_data[trial]) == 0:
            print 'TRIAL MISSING:', trial
            continue
        
        sanity_checks = [d.check_sanity(checks=[checkStarchContent]) for d in trial_data[trial]]
        sys.stderr.write('%i/%i items passed the sanity checks.\n' % (sum(map(int, sanity_checks)), len(sanity_checks)))        
        
        # calculate stats for the trial over all cultivars
        do_compute(PARAM_LIST, trial_data[trial], trial_params[trial])
        # print trial_params[trial]        
        for po in param_order:
            for so in stats_order:
                try:
                    row_data.append(str(trial_params[trial][po][so]))
                except:
                    pass
        fieldstats_out.write(','.join(row_data) + '\n')        
        
        # calculate stats for each cultivar separately
        trial_data[trial] = sorted(trial_data[trial], key=lambda x:x.key())
        for d in trial_data[trial]:
            print trial, d.subspeciesID
            subspecies_data[d.subspeciesID][trial] = subspecies_data[d.subspeciesID].get(trial, []) + [d] 
        
        # print subspecies_data[2673]
        # print subspecies_params[2673]
        # 2011: check cultivars missing!
        
        for k in subspecies_data:
            # print k, trial
            subspecies_params[k][trial] = {}
            do_compute(PARAM_LIST, subspecies_data[k][trial], subspecies_params[k][trial])
            # before you have a nervous breakdown again:
            # the difference to the median value is only required for starch yield            
            devFromLocMedianPlant = trial_params[trial]['starchYieldPlant']['median'] - subspecies_params[k][trial]['starchYieldPlant']['median']
            subspecies_params[k][trial]['devFromLocMedian_yieldPlant'] = devFromLocMedianPlant
            
            devFromLocMedianArea = trial_params[trial]['yieldPerHectar']['median'] - subspecies_params[k][trial]['yieldPerHectar']['median']
            subspecies_params[k][trial]['devFromLocMedian_yieldArea'] = devFromLocMedianArea
            for param in PARAM_LIST:
                subspecies_means[k][param].append(subspecies_params[k][trial][param]['mean'])
                subspecies_medians[k][param].append(subspecies_params[k][trial][param]['median'])        
        # end for trial  
        
    subspecies_rel_yields = {key : [] for key in subspecies_data} 
    for subspecies in subspecies_data:        
        all_yield_abs = []
        for tr in subspecies_data[subspecies]:
            all_yield_abs.extend([d.calculateStarch_abs() for d in subspecies_data[subspecies][tr]])
        
        all_yield_abs_median = compute_stats(all_yield_abs)['median']
        for tr in subspecies_params[subspecies]:
            median_yield =  subspecies_params[subspecies][tr]['starchYieldPlant']['median']
            # print subspecies, tr, median_yield, all_yield_abs_median, median_yield / all_yield_abs_median
            subspecies_rel_yields[subspecies].append(median_yield / all_yield_abs_median)
    
    for subspecies in sorted(subspecies_params.keys()):
        row_data = []
        for trial in TRIAL_D[trial_year]:
            row_data = [str(subspecies)]
            row_data.append(str(trial))
            row_data.append(str(trial_data[trial][0].location))
            row_data.append(str(trial_data[trial][0].n_plants))
            for po in param_order:
                for so in stats_order:
                    try:
                        row_data.append(str(subspecies_params[subspecies][trial][po][so]))
                    except:
                        pass
            row_data.append(str(subspecies_params[subspecies][trial]['devFromLocMedian_yieldPlant']))
            row_data.append(str(subspecies_params[subspecies][trial]['devFromLocMedian_yieldArea']))
            # if subspecies_params[k][trial]['devFromLocMedian_yieldPlant'] < 0:
            #    print '!!',  ','.join(row_data)
            # print '!!', subspecies_params[subspecies][trial]['devFromLocMedian_yieldPlant']
                
            fieldcult_out.write(','.join(row_data) + '\n')
        
    #print 'SUBSPECIES_PARAMS:'
    #for k in subspecies_params:
    #    for kk in subspecies_params[k]:
    #        print k, kk, subspecies_params[k][kk]
    
    # print 'SUBSPECIES_MEANS:', subspecies_means
    
    
    # print '****'    
    do_compute(PARAM_LIST, alltrials_data, alltrials_params)
    # print alltrials_params
    # print '****'    
    
    row_data = ['All', 'N/A', 'N/A', 'N/A']
    for po in param_order:
        for so in stats_order:
            try:
                row_data.append(str(alltrials_params[po][so]))
            except:
                pass
    fieldstats_out.write(','.join(row_data) + '\n')
    
    
    subspecies_global_params = {}
    row_data = []
    for k in subspecies_means:
        print 'K=', k
        row_data = [str(k)]
        subspecies_global_params[k] = {}        
        # do_compute(PARAM_LIST, subspecies_means[k], subspecies_global_params[k])
        # norm_factor:  subspecies_medians[k]['starchYieldPlant']
        
        
        
        for param in PARAM_LIST:
            print param, subspecies_means[k][param]
            subspecies_global_params[k][param] = compute_stats(subspecies_means[k][param])
        subspecies_global_params[k]['relYieldPlant'] = compute_stats(subspecies_rel_yields[k])
        # print subspecies_global_params[k]
        for po in param_order:
            for so in stats_order:
                row_data.append(str(subspecies_global_params[k][po][so]))
        globalcult_out.write(','.join(row_data) + '\n')
        
    globalcult_out.close()
    fieldcult_out.close()
    fieldstats_out.close()
    
    
    pass

if __name__ == '__main__': main(sys.argv[1:])
