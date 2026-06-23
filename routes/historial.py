from flask import Blueprint, render_template, request
from database.db import db
from modelos.evento import Evento
from modelos.historial import Historial
from sqlalchemy import extract

historial_bp = Blueprint(
    "historial",
    __name__
)


@historial_bp.route("/historial")
def historial():

    mes = request.args.get("mes", type=int)
    anio = request.args.get("anio", type=int)

    query = Historial.query

    if mes:
        query = query.filter(
            extract("month", Historial.fecha_registro) == mes
        )

    if anio:
        query = query.filter(
            extract("year", Historial.fecha_registro) == anio
        )

    movimientos = (
        query
        .order_by(Historial.fecha_registro.desc())
        .all()
    )

    registros = []

    for mov in movimientos:

        evento = mov.evento

        registros.append({
            "id": mov.id,
            "fecha": (
                mov.fecha_registro.strftime("%d/%m/%Y")
                if mov.fecha_registro else ""
            ),
            "hora": (
                mov.fecha_registro.strftime("%H:%M")
                if mov.fecha_registro else ""
            ),
            "sala": (
                ", ".join(
                    sala.nombre
                    for sala in evento.salas_asignadas
                )
                if evento and evento.salas_asignadas
                else "Sin asignar"
            ),
            "evento": (
                evento.nombre_evento
                if evento else "Evento eliminado"
            ),
            "estado": mov.accion
        })

    # Estadísticas filtradas
    query_eventos = Evento.query

    if mes:
        query_eventos = query_eventos.filter(
            extract("month", Evento.fecha) == mes
        )

    if anio:
        query_eventos = query_eventos.filter(
            extract("year", Evento.fecha) == anio
        )

    total_eventos = query_eventos.count()

    cancelados = query_eventos.filter(
        Evento.estado == "Cancelado"
    ).count()

    vigentes = total_eventos - cancelados

    cumplimiento = (
        round(vigentes / total_eventos * 100)
        if total_eventos > 0
        else 0
    )

    total_movimientos = query.count()

    modificaciones = query.filter(
        Historial.accion == "Modificado"
    ).count()

    return render_template(
        "historial.html",
        registros=registros,
        frecuencia_cambio=modificaciones,
        cumplimiento=f"{cumplimiento}%",
        optimizacion=total_movimientos,
        mes_actual=mes,
        anio_actual=anio
    )


@historial_bp.route("/historial/<int:id>")
def detalle(id):

    mov = db.get_or_404(Historial, id)

    return render_template(
        "historial_detalle.html",
        movimiento=mov
    )