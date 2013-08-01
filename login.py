import sys
# import _mysql
import MySQLdb

try:
    import cx_Oracle
except:
    sys.stderr.write('Import: Oracle driver missing in login.py\n')
    pass

DB_HOST = 'cosmos'
DB_USER = 'schudoma'
DB_PASS = 'christian*rules'
DB_NAME = 'trost_prod'
# DB_NAME = 'trost_prod_new'

DB_ORACLE = 'lims_read/jsbach@141.14.246.128:1521/naut90.mpimp-golm.mpg.de'

def get_db(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME):
    return MySQLdb.connect(host=host, user=user, passwd=passwd, db=db)
    

    


def get_ora_db():
    try:
        conn = cx_Oracle.Connection(DB_ORACLE)
        conn.current_schema = 'LIMS';
    except:
        sys.stderr.write('Oracle driver missing in login.py\n')
        sys.exit(1)

    return conn
