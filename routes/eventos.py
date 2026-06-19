
from datetime import date, time

from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import db
from modelos.evento import Evento
from modelos.sala import Sala
from modelos.historial import Historial


eventos_bp = Blueprint(
    "eventos",
    __name__
)


def _parse_fecha(valor):
    return date.fromisoformat(valor) if valor else None


def _parse_hora(valor):
    if not valor:
        return None
    # <input type="time"> envía "HH:MM" o "HH:MM:SS"
    partes = valor.split(":")
    return time(int(partes[0]), int(partes[1]),
                int(partes[2]) if len(partes) > 2 else 0)


def _datos_form():
    """Lee los campos del formulario de evento y los devuelve en un dict."""
    return dict(
        responsable      = request.form.get("responsable"),
        nombre_evento    = request.form.get("nombre_evento"),
        asistentes       = request.form.get("asistentes", type=int),
        fecha            = _parse_fecha(request.form.get("fecha")),
        hora_inicio      = _parse_hora(request.form.get("hora_inicio")),
        hora_fin         = _parse_hora(request.form.get("hora_fin")),
        tipo_acomodo     = request.form.get("tipo_acomodo"),
        # checkboxes: presentes en el form = True, ausentes = False
        extension        = "extension"        in request.form,
        cafeteria        = "cafeteria"        in request.form,
        sonido           = "sonido"           in request.form,
        videoconferencia = "videoconferencia" in request.form,
        sala_id          = request.form.get("sala_id", type=int),
    )


@eventos_bp.route("/registrar", methods=["GET", "POST"])
def registrar():
    salas = Sala.query.all()  # para el selector de sala

    if request.method == "POST":
        nuevo_evento = Evento(estado="Activo", **_datos_form())

        try:
            db.session.add(nuevo_evento)
            db.session.flush()  # para obtener el id antes del commit

            db.session.add(Historial(
                evento_id=nuevo_evento.id,
                accion="Original",
                descripcion="Evento registrado en el sistema."
            ))

            db.session.commit()
            flash("Evento registrado correctamente.", "success")
            return redirect(url_for("calendar.calendario"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar el evento: {e}", "danger")

    return render_template("registrar_evento.html", salas=salas)


@eventos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    evento = Evento.query.get_or_404(id)
    salas = Sala.query.all()

    if request.method == "POST":
        datos = _datos_form()

        # Detectamos qué campos cambiaron para describir la modificación
        cambios = [
            campo
            for campo, valor in datos.items()
            if getattr(evento, campo) != valor
        ]

        for campo, valor in datos.items():
            setattr(evento, campo, valor)

        # Un evento cancelado no vuelve a "Modificado"; el resto sí
        if evento.estado != "Cancelado":
            evento.estado = "Modificado"

        try:
            db.session.add(Historial(
                evento_id=evento.id,
                accion="Modificado",
                descripcion=(
                    "Se modificaron: " + ", ".join(cambios)
                    if cambios else "Se guardó el evento sin cambios."
                )
            ))
            db.session.commit()
            flash("Evento actualizado correctamente.", "success")
            return redirect(url_for("calendar.calendario"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar el evento: {e}", "danger")

    # GET: mostramos el formulario con los datos actuales del evento
    return render_template(
        "registrar_evento.html",
        salas=salas,
        evento=evento,
        editando=True,
        responsable=evento.responsable,
        nombre_evento=evento.nombre_evento,
        asistentes=evento.asistentes,
        fecha=evento.fecha.isoformat() if evento.fecha else "",
        hora_inicio=evento.hora_inicio.strftime("%H:%M") if evento.hora_inicio else "",
        hora_fin=evento.hora_fin.strftime("%H:%M") if evento.hora_fin else "",
        tipo_acomodo=evento.tipo_acomodo,
        sala_id=evento.sala_id,
        extension=evento.extension,
        cafeteria=evento.cafeteria,
        sonido=evento.sonido,
        videoconferencia=evento.videoconferencia,
    )


@eventos_bp.route("/cancelar/<int:id>", methods=["POST"])
def cancelar(id):
    evento = Evento.query.get_or_404(id)
    evento.estado = "Cancelado"

    try:
        db.session.add(Historial(
            evento_id=evento.id,
            accion="Cancelado",
            descripcion="El evento fue cancelado."
        ))
        db.session.commit()
        flash("Evento cancelado.", "warning")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al cancelar el evento: {e}", "danger")

    return redirect(url_for("calendar.calendario"))
