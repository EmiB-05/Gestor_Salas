from flask import Blueprint, render_template
from modelos.evento import Evento

calendar_bp = Blueprint(
    "calendar",
    __name__
)

@calendar_bp.route("/")
def calendario():

    eventos_db = Evento.query.all()

    eventos = []

    for evento in eventos_db:

        eventos.append({
            "id": evento.id,
            "title": evento.nombre_evento,
            "start": f"{evento.fecha}T{evento.hora_inicio}",
            "end": f"{evento.fecha}T{evento.hora_fin}",
            "responsable": evento.responsable,
            "asistentes": evento.asistentes,
            "estado": evento.estado,
            "tipo_acomodo": evento.tipo_acomodo,
            "sala": evento.sala.nombre if evento.sala else "Sin asignar"
        })

    return render_template(
        "calendario.html",
        eventos=eventos
    )