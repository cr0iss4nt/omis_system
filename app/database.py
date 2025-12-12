import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from app.config import Config
import logging

logger = logging.getLogger(__name__)

# Увеличим пул соединений
pool = SimpleConnectionPool(1, 20, dsn=Config.DATABASE_URL)

@contextmanager
def get_db_connection():
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        pool.putconn(conn)

@contextmanager
def get_db_cursor():
    with get_db_connection() as conn:
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()