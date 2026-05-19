import mysql.connector
import streamlit as st

DB_CONFIG = {
    "host": st.secrets["DB_HOST"],
    "port": st.secrets["DB_PORT"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "database": st.secrets["DB_NAME"],
}

# Cache a SINGLE connection instead of a pool
@st.cache_resource
def get_connection():
    try:
        # This opens one connection and keeps it open for the entire app session
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None