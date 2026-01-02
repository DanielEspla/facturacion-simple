from flask import Flask, render_template, request, redirect
import os
from datetime import date
import psycopg2

app = Flask(__name__, template_folder="templates")

DATABASE_URL = os.environ.get("DATABASE_URL")

@app.route("/health")
def health():
    return {
        "status": "ok",
        "database_url_exists": DATABASE_URL is not None
    }

def get_conn():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL no existe en el entorno")
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS facturas (
            id SERIAL PRIMARY KEY,
            numero TEXT NOT NULL,
            fecha TEXT NOT NULL,
            cliente TEXT NOT NULL,
            concepto TEXT NOT NULL,
            base NUMERIC NOT NULL,
            iva NUMERIC NOT NULL,
