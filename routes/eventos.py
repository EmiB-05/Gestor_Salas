from flask import Blueprint
from flask import render_template

eventos_bp = Blueprint(
    "eventos",
    __name__
)

@eventos_bp.route("/")
def inicio():

    return render_template(
        "calendario.html"
    )