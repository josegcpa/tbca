import os
import psycopg2

conn_wbc = psycopg2.connect(
    database="tbca-wbc",
    user=os.getenv("db_root_username"),
    password=os.getenv("db_root_password"),
    host=os.getenv("postgres_host"),
    port=os.getenv("postgres_port"))

conn_rbc = psycopg2.connect(
    database="tbca-rbc",
    user=os.getenv("db_root_username"),
    password=os.getenv("db_root_password"),
    host=os.getenv("postgres_host"),
    port=os.getenv("postgres_port"))

conn_users = psycopg2.connect(
    database="users",
    user=os.getenv("db_root_username"),
    password=os.getenv("db_root_password"),
    host=os.getenv("postgres_host"),
    port=os.getenv("postgres_port"))
