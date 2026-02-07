from config import DIRECT_URL
import psycopg2
import os

DATABASE_URL = DIRECT_URL

conn = psycopg2.connect(dsn=DATABASE_URL, sslmode="require")
cur = conn.cursor()

cur.execute("SELECT now();")
print(cur.fetchone())

cur.close()
conn.close()
