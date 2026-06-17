from flask import Blueprint, url_for
from flask import render_template

from modelos.evento import Evento

eventos_bp = Blueprint(
    "eventos",
    __name__
)


@eventos_bp.route("/registrar")
def registrar():
    return render_template("registrar_evento.html")


