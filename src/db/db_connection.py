# Database connection management with Streamlit caching and reconnection handling
import mariadb
import streamlit as st


@st.cache_resource
def get_connection_pool():
    """
    Creates and caches a MariaDB connection pool.
    Uses @st.cache_resource so the pool persists across Streamlit reruns
    and is shared by all users/sessions.
    """
    try:
        pool = mariadb.ConnectionPool(
            pool_name="lto_pool",
            pool_size=5,
            host=st.secrets.DB_CREDENTIALS.DB_HOST,
            user=st.secrets.DB_CREDENTIALS.DB_USER,
            password=st.secrets.DB_CREDENTIALS.DB_PASSWORD,
            database=st.secrets.DB_CREDENTIALS.DB_NAME,
            port=int(st.secrets.DB_CREDENTIALS.DB_PORT),
        )
        return pool
    except mariadb.Error as e:
        st.error(f"Failed to create database connection pool: {e}")
        return None


def get_connection():
    """
    Retrieves a connection from the pool.
    Each service function should call this, use the connection, then close it
    to return it to the pool.
    """
    pool = get_connection_pool()
    if pool is None:
        raise ConnectionError("Database connection pool is not available.")
    try:
        conn = pool.get_connection()
        return conn
    except mariadb.Error as e:
        # Pool may be stale — clear the cached resource and retry once
        get_connection_pool.clear()
        pool = get_connection_pool()
        if pool is None:
            raise ConnectionError(f"Database reconnection failed: {e}")
        return pool.get_connection()


def execute_query(query, params=None, fetch=True):
    """
    Executes a read query and returns results as a list of dicts.
    Automatically manages connection lifecycle (acquire → execute → release).

    Args:
        query: SQL query string with ? placeholders.
        params: Tuple of parameter values.
        fetch: If True, returns fetched rows. If False, returns None (for writes).

    Returns:
        List of dicts for SELECT queries, or None for writes.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())

        if fetch:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            conn.commit()
            return cursor.rowcount
    except mariadb.Error as e:
        if not fetch:
            conn.rollback()
        raise e
    finally:
        conn.close()
