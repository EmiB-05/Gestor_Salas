from flask import Blueprint, render_template

estadisticas_bp = Blueprint(
    "estadisticas",
    __name__
)

@estadisticas_bp.route("/estadisticas")
def estadisticas():

    return render_template(
        "estadisticas.html",

        total_eventos=25,

        total_salas=3,

        promedio_asistentes=34,

        cancelados=2
    )