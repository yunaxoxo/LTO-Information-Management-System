# Establish database connection here 
from mysql.connector import pooling
import streamlit as  st

#reference: https://dev.mysql.com/doc/connector-python/en/connector-python-connection-pooling.html 
# Establish conenction pool to the database
# Use later for executing queries in the controllers

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root', #change this to your own password
    'database': 'lto_system'
} 

#Create a connection pool 
@st.cache_resource
def get_connection_pool():
    try: 
        pool = pooling.MySQLConnectionPool(pool_name="lto_pool", pool_size=5, **DB_CONFIG)
        return pool
    except Exception as e:
        st.error(f"Error creating connection pool: {e}")
        return None

def get_connection():
    pool = get_connection_pool()
    if pool:
       return pool.get_connection()
    else:
        return None