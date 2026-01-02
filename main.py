from flask import Flask, render_template, request, redirect
import os
from datetime import date
import psycopg

app = Flask(__name__, template_folder="templates")

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL no existe en el entorno")
    return psycopg.connect(DATABASE_URL)

def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
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

def obtener_facturas():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT numero, fecha, cliente, concepto, base, iva, total
                FROM facturas
                ORDER BY id ASC;
            """)
            rows = cur.fetchall()

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

def siguiente_numero_factura(año):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT numero
                FROM facturas
                WHERE numero LIKE %s
                ORDER BY id DESC
                LIMIT 1;
            """, (f"{año}-%",))
            row = cur.fetchone()

    if not row:
        return f"{año}-1"

    ultimo = int(row[0].split("-")[1])
    return f"{año}-{ultimo + 1}"

@app.route("/health")
def health():
    return {
        "status": "ok",
        "database": DATABASE_URL is not None
    }

@app.route("/", methods=["GET", "POST"])
def index():
    try:
        init_db()

        if request.method == "POST":
            cliente = request.form["cliente"]
            concepto = request.form["concepto"]
            base = float(request.form["base"])

            iva = round(base * 0.21, 2)
            total = round(base + iva, 2)

            hoy = date.today()
            fecha = hoy.strftime("%d-%m-%Y")
            año = hoy.year
            numero = siguiente_numero_factura(año)

            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO facturas (numero, fecha, cliente, concepto, base, iva, total)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """, (numero, fecha, cliente, concepto, base, iva, total))

            return redirect("/")

        facturas = obtener_facturas()
        return render_template("index.html", facturas=facturas)

    except Exception as e:
        return f"<h1>Error interno</h1><pre>{e}</pre>", 500

@app.route("/<path:path>")
def catch_all(path):
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
