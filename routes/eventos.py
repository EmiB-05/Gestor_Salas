
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import db
from modelos.evento import Evento
from modelos.sala import Sala


eventos_bp = Blueprint(
    "eventos",
    __name__
)

@eventos_bp.route("/registrar", methods=["GET", "POST"])
def registrar():
    salas = Sala.query.all()  # para el selector de sala

    if request.method == "POST":
        nuevo_evento = Evento(
            responsable      = request.form.get("responsable"),
            nombre_evento    = request.form.get("nombre_evento"),
            asistentes       = request.form.get("asistentes", type=int),
            fecha            = request.form.get("fecha"),
            hora_inicio      = request.form.get("hora_inicio"),
            hora_fin         = request.form.get("hora_fin"),
            tipo_acomodo     = request.form.get("tipo_acomodo"),
            estado           = "pendiente",
            # checkboxes: presentes en el form = True, ausentes = False
            extension        = "extension"        in request.form,
            cafeteria        = "cafeteria"        in request.form,
            sonido           = "sonido"           in request.form,
            videoconferencia = "videoconferencia" in request.form,
            sala_id          = request.form.get("sala_id", type=int),
        )

        try:
            db.session.add(nuevo_evento)
            db.session.commit()
            flash("Evento registrado correctamente.", "success")
            return redirect(url_for("calendar/calendario"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar el evento: {e}", "danger")

    return render_template("registrar_evento.html", salas=salas)