from flask import Blueprint, render_template
from sqlalchemy import func
from database.db import db
from modelos.evento import Evento
from modelos.sala import Sala

estadisticas_bp = Blueprint(
    "estadisticas",
    __name__
)

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


@estadisticas_bp.route("/estadisticas")
def estadisticas():

    total_eventos = Evento.query.count()
    cancelados = Evento.query.filter_by(estado="Cancelado").count()

    salas = Sala.query.order_by(Sala.id).all()
    eventos = Evento.query.all()
    conteo_por_sala = {sala.id: 0 for sala in salas}
    for evento in eventos:
        for sala in evento.salas_asignadas:
            conteo_por_sala[sala.id] += 1
    total_salas = sum(1 for cantidad in conteo_por_sala.values() if cantidad)

    promedio = db.session.query(func.avg(Evento.asistentes)).scalar()
    promedio_asistentes = round(promedio) if promedio else 0

    # --- Eventos por sala ---
    salas_labels = [sala.nombre for sala in salas]
    salas_data = [conteo_por_sala[sala.id] for sala in salas]

    # --- Estado de eventos ---
    estados = ["Activo", "Modificado", "Cancelado"]
    conteo_estados = dict(
        db.session.query(Evento.estado, func.count(Evento.id))
        .group_by(Evento.estado)
        .all()
    )
    estado_data = [conteo_estados.get(e, 0) for e in estados]

    # --- Asistentes por mes (12 meses) ---
    asistentes_mes = [0] * 12
    filas = (
        db.session.query(
            func.extract("month", Evento.fecha),
            func.sum(Evento.asistentes),
        )
        .filter(Evento.fecha.isnot(None))
        .group_by(func.extract("month", Evento.fecha))
        .all()
    )
    for mes, suma in filas:
        if mes:
            asistentes_mes[int(mes) - 1] = int(suma or 0)

    return render_template(
        "estadisticas.html",
        total_eventos=total_eventos,
        total_salas=total_salas,
        promedio_asistentes=promedio_asistentes,
        cancelados=cancelados,
        salas_labels=salas_labels,
        salas_data=salas_data,
        estado_labels=estados,
        estado_data=estado_data,
        meses_labels=MESES,
        asistentes_data=asistentes_mes,
    )
