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
