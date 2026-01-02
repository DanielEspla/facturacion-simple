import os
from flask import Flask, render_template, request, redirect
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no existe en el entorno")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True)
    numero = Column(String, nullable=False)
    fecha = Column(Date, nullable=False)
    cliente = Column(String, nullable=False)
    concepto = Column(String, nullable=False)
    base = Column(Float, nullable=False)
    iva = Column(Float, nullable=False)
    total = Column(Float, nullable=False)

Base.metadata.create_all(engine)

def siguiente_numero_factura():
    year = datetime.now().year
    ultima = session.query(Factura).filter(
        Factura.numero.like(f"{year}-%")
    ).order_by(Factura.id.desc()).first()

    if not ultima:
        return f"{year}-1"

    ultimo_num = int(ultima.numero.split("-")[1])
    return f"{year}-{ultimo_num + 1}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        cliente = request.form["cliente"]
        concepto = request.form["concepto"]
        base = float(request.form["base"])

        iva = round(base * 0.21, 2)
        total = round(base + iva, 2)

        factura = Factura(
            numero=siguiente_numero_factura(),
            fecha=datetime.now().date(),
            cliente=cliente,
            concepto=concepto,
            base=base,
            iva=iva,
            total=total
        )

        session.add(factura)
        session.commit()

        return redirect("/")

    facturas = session.query(Factura).order_by(Factura.id).all()
    return render_template("index.html", facturas=facturas)

if __name__ == "__main__":
    app.run()
