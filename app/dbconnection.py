import psycopg2
import MySQLdb
import time
# import pyodbc


def executeQuery(query, dbType, dbName):

    start = time.time()
    if dbType.lower() == "redshift":
        with psycopg2.connect("dbname={0} host=redshift-server-instacart.cxrld0xhd2yp.us-east-1.redshift.amazonaws.com port=5439 user=admin1 password=12345abcdE".format(dbName)) as con:
            with con.cursor() as cur:
                cur.execute(query)
                tableHeaders = [i[0] for i in cur.description]
                results = cur.fetchall()
                end = time.time()
                return tableHeaders, results, end-start
    elif dbType.lower() == "rds":
        with MySQLdb.connect(host="instacart.ctn7lp6tviib.us-east-1.rds.amazonaws.com", user="admin1", passwd="12345abcdE", db=dbName) as con:
            with con.cursor() as cur:
                cur.execute(query)
                tableHeaders = [i[0] for i in cur.description]
                results = cur.fetchall()
                end = time.time()
                return tableHeaders, results, end-start
    end = time.time()
    return [], [], end-start




                