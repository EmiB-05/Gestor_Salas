from flask import Blueprint, render_template

historial_bp = Blueprint(
    "historial",
    __name__
)

@historial_bp.route("/historial")
def historial():

    registros = []

    return render_template(
        "historial.html",
        registros=registros,
        frecuencia_cambio=12,
        cumplimiento_eventos=75,
        optimizacion=15
    )