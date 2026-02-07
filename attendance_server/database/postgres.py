import psycopg2 
from contextlib import contextmanager
from config import DIRECT_URL

# Initialize PostgreSQL connection pool


@contextmanager
def get_db_cursor():

    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(dsn=DIRECT_URL, sslmode="require")
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

