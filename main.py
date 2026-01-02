from flask import Flask, render_template, request, redirect
import os
from datetime import date
import psycopg2

# Flask configurado correctamente para Railway
app = Flask(__name__, template_folder="templates")

# Variable que Railway inyecta automáticamente
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

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
            total NUMERIC NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def obtener_facturas():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT numero, fecha, cliente, concepto, base, iva, total
        FROM facturas
        ORDER BY id ASC;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    facturas = []
    for r in rows:
        facturas.append({
            "numero": r[0],
            "fecha": r[1],
            "cliente": r[2],
            "concepto": r[3],
            "base": float(r[4]),
            "iva": float(r[5]),
            "total": float(r[6]),
        })
    return facturas

def siguiente_numero_factura(año):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT numero
        FROM facturas
        WHERE numero LIKE %s
        ORDER BY id DESC
        LIMIT 1;
    """, (f"{año}-%",))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return f"{año}-1"

    ul
