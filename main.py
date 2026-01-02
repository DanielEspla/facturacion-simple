from flask import Flask, render_template, request, redirect
import json
import os
from datetime import date

app = Flask(__name__, template_folder="templates")

DATA_FILE = "facturas.json"

def cargar_facturas():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def guardar_facturas(facturas):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(facturas, f, indent=2, ensure_ascii=False)

def siguiente_numero_factura(facturas, year):
    del_año = [f for f in facturas if f["numero"].startswith(f"{year}-")]
    if not del_año:
        return f"{year}-1"
    ultimo = max(int(f["numero"].split("-")[1]) for f in del_año)
    return f"{year}-{ultimo + 1}"

@app.route("/", methods=["GET", "POST"])
def index():
    facturas = cargar_facturas()

    if request.method == "POST":
        cliente = request.form["cliente"]
        concepto = request.form["concepto"]
        base = float(request.form["base"])

        iva = round(base * 0.21, 2)
        total = round(base + iva, 2)

        hoy = date.today()
        fecha = hoy.strftime("%d-%m-%Y")
        numero = siguiente_numero_factura(facturas, hoy.year)

        facturas.append({
            "numero": numero,
            "fecha": fecha,
            "cliente": cliente,
            "concepto": concepto,
            "base": base,
            "iva": iva,
            "total": total
        })

        guardar_facturas(facturas)
        return redirect("/")

    return render_template("index.html", facturas=facturas)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
