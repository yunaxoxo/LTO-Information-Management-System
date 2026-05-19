import mysql.connector
from mysql.connector import pooling
import streamlit as st

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "VladMel@28!",
    "database": "lto_system",
}

@st.cache_resource
def get_connection_pool():
    try:
        pool = pooling.MySQLConnectionPool(
            pool_name="lto_pool",
            pool_size=5,
            **DB_CONFIG
        )
        return pool
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return None

def get_connection():
    pool = get_connection_pool()
    if pool:
<<<<<<< Updated upstream
       return pool.get_connection()
    else:
        return None

# DATABASE connection logic
import streamlit as st

DB_CONFIG = {
    "host": st.secrets["DB_HOST"],
    "port": st.secrets["DB_PORT"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "database": st.secrets["DB_NAME"],
}

=======
        return pool.get_connection()
    return None

def execute_query(query, params=None, fetch=True):
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def execute_many(query, params_list):
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
#
>>>>>>> Stashed changes
