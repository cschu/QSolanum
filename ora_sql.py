#!/usr/bin/python

import os
import sys
import math

import login
_odb = login.get_ora_db()

aliquots_q = """
SELECT aliquot_id, u_culture from aliquot_user where u_culture = :study_id
""".strip()

culture_q = """
SELECT u_culture FROM aliquot_user WHERE aliquot_id = :aliquot_id
""".strip()

subspecies_q = """
select sample_user.u_subspecies_id, aliquot.aliquot_id, aliquot.name, aliquot_user.u_culture
from aliquot
join aliquot_user on aliquot.aliquot_id = aliquot_user.aliquot_id
join study_user on study_user.study_id = aliquot_user.u_culture
left join sample_user on sample_user.sample_id = aliquot.sample_id
where study_user.u_project = 'TROST'
AND aliquot.aliquot_id = :aliquot_id
""".strip()

def get_plant_information(aliquot_id):
    c = _odb.cursor()
    c.execute(subspecies_q, dict(aliquot_id=aliquot_id))
    row = c.fetchall()
    if len(row) > 0:
        return {
            'name'          : row[0][2],
            'aliquot_id'    : row[0][1],
            'subspecies_id' : row[0][0],
            'culture_id'    : row[0][3],
        }
    return None

def get_subspecies_id(aliquot_id):
    c = _odb.cursor()
    c.execute(subspecies_q, dict(aliquot_id=aliquot_id))
    row = c.fetchall()
    if len(row) > 0:
        if len(row[0]) > 0:
            return row[0][0]
    return None

def get_culture_id(aliquot_id):
    c = _odb.cursor()
    c.execute(culture_q, dict(aliquot_id=aliquot_id))
    row = c.fetchall()
    if len(row) > 0:
        if len(row[0]) > 0:
            return row[0][0]
    return None

def get_aliquots(limsstudy_id):
    c = _odb.cursor()
    c.execute(aliquots_q, dict(study_id=limsstudy_id))
    rows = c.fetchall()
#    for row in rows:
#        print int(row[0])
    return [row[0] for row in c]

###
def main(argv):
    return None

if __name__ == '__main__': main(sys.argv[1:])
