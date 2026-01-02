from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)

FACTURAS_FILE = "facturas.json"

def cargar_facturas():
    if not os.path.exists(FACTURAS_FILE):
        return []
    with open(FACTURAS_FILE, "r") as f:
        return json.load(f)

def guardar_facturas(facturas):
    with open(FACTURAS_FILE, "w") as f:
        json.dump(facturas, f, indent=4)

@app.route("/", methods=["GET", "POST"])
def index():
    facturas = cargar_facturas()

    if request.method == "POST":
        cliente = request.form["cliente"]
        concepto = request.form["concepto"]
        base = float(request.form["base"])
        iva = round(base * 0.21, 2)
        total = round(base + iva, 2)

        factura = {
            "cliente": cliente,
            "concepto": concepto,
            "base": base,
            "iva": iva,
            "total": total
        }

        facturas.append(factura)
        guardar_facturas(facturas)

        return redirect("/")

    return render_template("index.html", facturas=facturas)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
