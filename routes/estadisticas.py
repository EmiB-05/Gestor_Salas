from flask import Blueprint, render_template, request
from sqlalchemy import func, extract

from database.db import db
from modelos.evento import Evento
from modelos.sala import Sala


estadisticas_bp = Blueprint(
    "estadisticas",
    __name__
)

MESES = [
    "Ene", "Feb", "Mar", "Abr",
    "May", "Jun", "Jul", "Ago",
    "Sep", "Oct", "Nov", "Dic"
]


@estadisticas_bp.route("/estadisticas")
def estadisticas():

    # -------------------------
    # FILTROS
    # -------------------------

    mes = request.args.get("mes", type=int)
    anio = request.args.get("anio", type=int)

    if not anio:
        anio = 2026

    query = Evento.query.filter(
        extract("year", Evento.fecha) == anio
    )

    if mes:
        query = query.filter(
            extract("month", Evento.fecha) == mes
        )

    eventos = query.all()

    # -------------------------
    # TARJETAS
    # -------------------------

    total_eventos = len(eventos)

    cancelados = sum(
        1
        for evento in eventos
        if evento.estado == "Cancelado"
    )

    asistentes_totales = sum(
        evento.asistentes or 0
        for evento in eventos
    )

    promedio_asistentes = round(
        asistentes_totales / total_eventos
    ) if total_eventos else 0

    # -------------------------
    # EVENTOS POR SALA
    # -------------------------

    salas = Sala.query.order_by(
        Sala.id
    ).all()

    conteo_por_sala = {
        sala.id: 0
        for sala in salas
    }

    for evento in eventos:

        if hasattr(evento, "salas_asignadas"):

            for sala in evento.salas_asignadas:
                conteo_por_sala[sala.id] += 1

        elif evento.sala:
            conteo_por_sala[evento.sala.id] += 1

    salas_labels = [
        sala.nombre
        for sala in salas
    ]

    salas_data = [
        conteo_por_sala[sala.id]
        for sala in salas
    ]

    # -------------------------
    # ESTADO DE EVENTOS
    # -------------------------

    estados = [
        "Activo",
        "Modificado",
        "Cancelado"
    ]

    estado_data = [
        sum(
            1
            for e in eventos
            if e.estado == "Activo"
        ),

        sum(
            1
            for e in eventos
            if e.estado == "Modificado"
        ),

        sum(
            1
            for e in eventos
            if e.estado == "Cancelado"
        )
    ]

    # -------------------------
    # ASISTENTES
    # -------------------------

    if not mes:

        asistentes_labels = MESES

        asistentes_data = [0] * 12

        filas = (
            db.session.query(
                extract("month", Evento.fecha),
                func.sum(Evento.asistentes)
            )
            .filter(
                extract("year", Evento.fecha) == anio
            )
            .group_by(
                extract("month", Evento.fecha)
            )
            .all()
        )

        for m, suma in filas:

            asistentes_data[
                int(m) - 1
            ] = int(suma or 0)

        titulo_asistentes = "Asistentes por Mes"

    else:

        asistentes_labels = [
            "Semana 1",
            "Semana 2",
            "Semana 3",
            "Semana 4",
            "Semana 5"
        ]

        asistentes_data = [
            0, 0, 0, 0, 0
        ]

        for evento in eventos:

            if not evento.fecha:
                continue

            dia = evento.fecha.day

            semana = min(
                (dia - 1) // 7,
                4
            )

            asistentes_data[semana] += (
                evento.asistentes or 0
            )

        titulo_asistentes = "Asistentes por Semana"

    # -------------------------
    # TEMPLATE
    # -------------------------

    return render_template(
        "estadisticas.html",

        mes_actual=mes,
        anio_actual=anio,

        total_eventos=total_eventos,
        asistentes_totales=asistentes_totales,
        promedio_asistentes=promedio_asistentes,
        cancelados=cancelados,

        salas_labels=salas_labels,
        salas_data=salas_data,

        estado_labels=estados,
        estado_data=estado_data,

        asistentes_labels=asistentes_labels,
        asistentes_data=asistentes_data,
        titulo_asistentes=titulo_asistentes
    )