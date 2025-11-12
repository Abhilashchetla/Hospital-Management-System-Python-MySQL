import mysql.connector

def get_connection():
    con = mysql.connector.connect(
        host="localhost",
        user="root",          
        password="Abhi123@",  
        database="mini_project"
    )
    return con
