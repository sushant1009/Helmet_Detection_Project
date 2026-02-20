import psycopg2 
from contextlib import contextmanager
from config import DIRECT_URL
# from utils.logger import setup_logger

# logger = setup_logger("database.postgres")


@contextmanager
def get_db_cursor():

    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(dsn=DIRECT_URL, sslmode="require")
        cursor = conn.cursor()
        # logger.info("PostgreSQL connection established")
        yield cursor
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        # logger.error(f"Database error: {e}")
        raise e
    finally:
        if cursor:
            cursor.close()
            # logger.info("PostgreSQL cursor closed")
        if conn:
            conn.close()
            # logger.info("PostgreSQL connection closed")

