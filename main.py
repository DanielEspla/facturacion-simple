from flask import Flask, render_template, request, redirect
import os
from datetime import date
import psycopg2

app = Flask(__name__)

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

    return [
        {
            "numero": r[0],
            "fecha": r[1],
            "cliente": r[2],
            "concepto": r[3],
            "base": float(r[4]),
            "iva": float(r[5]),
            "total": float(r[6]),
        }
        for r in rows
    ]

def siguiente_numero_factura(año_actual):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT numero FROM facturas
        WHERE numero LIKE %s
        ORDER BY id DESC
        LIMIT 1;
    """, (f"{año_actual}-%",))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return f"{año_actual}-1"

    ultimo = int(row[0].split("-")[1])
    return f"{año_actual}-{ultimo + 1}"

@app.route("/", methods=["GET", "POST"])
def index():
    init_db()

    if request.method == "POST":
        cliente = request.form["cliente"]
        concepto = request.form["concepto"]
        base = float(request.form["base"])

        iva = round(base * 0.21, 2)
        total = round(base + iva, 2)

        hoy = date.today()
        fecha = hoy.strftime("%d-%m-%Y")
        año_actual = hoy.year
        numero = siguiente_numero_factura(año_actual)

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO facturas (numero, fecha, cliente, concepto, base, iva, total)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (numero, fecha, cliente, concepto, base, iva, total))
        conn.commit()
        cur.close()
        conn.close()

        return redirect("/")

    facturas = obtener_facturas()
    return render_template("index.html", facturas=facturas)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
