# db.py
import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="cinema_db",
        user="cinema_user",
        password="cinema_pass",
        host="localhost",
        port=5432
    )
