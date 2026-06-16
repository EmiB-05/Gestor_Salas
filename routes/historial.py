@historial_bp.route("/historial")
def historial():

    registros = []

    return render_template(
        "historial.html",
        registros=registros,
        frecuencia_cambio=None,
        cumplimiento_eventos=None,
        optimizacion=None
    )