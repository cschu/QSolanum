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
