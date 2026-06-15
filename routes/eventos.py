from flask import Blueprint
from flask import render_template

eventos_bp = Blueprint(
    "eventos",
    __name__
)

@eventos_bp.route("/")
def inicio():
    return render_template("calendario.html")

@eventos_bp.route("/registrar")
def registrar():
    return render_template("registrar.html")

@eventos_bp.route("/estadisticas")
def estadisticas():
    return render_template("estadisticas.html")

@eventos_bp.route("/historial")
def historial():
    return render_template("historial.html")