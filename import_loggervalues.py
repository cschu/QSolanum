#!/usr/bin/env python
'''
Created on Sep 5, 2013

@author: Christian Schudoma (schudoma@mpimp-golm.mpg.de, cschu@darkjade.net)
'''
import sys
import re
import os

import login
TROST_DB = login.get_db(db='trost_prod')
TROST_C = TROST_DB.cursor()

from import_logger import convert_date

VALUES = {'M': 293, 'T': 292}

LOGGER_PLANT_QUERY = """ 
SELECT 
logger.id AS log_id,
PP.plant_id AS plant_id
FROM logger 
JOIN phenotypes P ON logger.id = P.number
JOIN phenotype_plants PP ON PP.phenotype_id = P.id 
WHERE
logger.start <= '%s' AND
logger.end >= '%s' AND
logger.logger = %i AND
logger.channel = %i AND
P.value_id = 294 
""".strip().replace('\n', ' ')

CHECK_TIMESTAMP_QUERY = """
SELECT COUNT(*)
FROM logger
WHERE logger.logger = %i AND
logger.start <= '%s' AND
logger.end >= '%s'
""".strip().replace('\n', ' ')

INSERT_SENSOR_VALUE = """
INSERT INTO phenotypes VALUES (NULL, NULL, 'USER_DEFINED', 4, '%s', '%s', NULL, 812, %i, %s);
""".strip().replace('\n', ' ')

SET_LINKS = """
INSERT INTO phenotype_plants VALUES (NULL, %i, LAST_INSERT_ID());
""".strip().replace('\n', ' ')

def process_file(fn):
    logger = int(os.path.basename(fn).split('_')[0][-1])
        
    headers = None
    for line in open(fn):
        line = line.strip().replace('" "', 'NULL')
        line = re.split(' +', line)        
        if headers is None:
            headers = line
            continue
        dline = dict(zip(headers, line))
        d, t = dline['Date_Time'].split('_')
        timestamp = ' '.join([convert_date(d), t])
        del dline['Date_Time']
        
        TROST_C.execute(CHECK_TIMESTAMP_QUERY % (logger, timestamp, timestamp))        
        n_records = int(TROST_C.fetchall()[0][0])
        if n_records == 0:
            continue
        for k in dline:            
            cid, vid = int(k[1:-1]), VALUES[k[-1]]
            TROST_C.execute(LOGGER_PLANT_QUERY % (timestamp, timestamp, logger, cid))
            row = TROST_C.fetchall()
            if len(row) > 1:
                sys.stderr.write(' '.join(map(str, ['AMBIGUITY!', timestamp, logger, k, cid, dline[k], vid, row])))
                print 'ROLLBACK;'
                sys.exit()
            if len(row) == 1:
                log_id, plant_id = map(int, row[0])
                # print timestamp, logger, k, vid, cid, dline[k], # logger_plant['log_id'], logger_plant['plant_id']
                # print log_id, plant_id
                cmd = INSERT_SENSOR_VALUE % (convert_date(d), t, vid, str(dline[k]))
                print cmd
                cmd = SET_LINKS % plant_id
                print cmd
    pass        
    

def main(argv):
    
    print 'START TRANSACTION;'
    print 'SET autocommit = 0;'
    
    for fn in argv:
        process_file(fn)       
            
    print 'COMMIT;'
    
    
    pass

if __name__ == '__main__': 
    main(sys.argv[1:])
    TROST_DB.close()
