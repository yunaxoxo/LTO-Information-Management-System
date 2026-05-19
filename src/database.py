import mysql.connector
import streamlit as st

DB_CONFIG = {
    "host": st.secrets["DB_HOST"],
    "port": st.secrets["DB_PORT"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "database": st.secrets["DB_NAME"],
}

@st.cache_resource
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None