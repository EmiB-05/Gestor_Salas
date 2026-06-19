
from datetime import date, time

from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
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
        responsable      = request.form.get("responsable", "").strip(),
        nombre_evento    = request.form.get("nombre_evento", "").strip(),
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
    )


def _ids_salas_form():
    valores = request.form.getlist("sala_ids")
    # Compatibilidad con formularios o clientes anteriores.
    if not valores and request.form.get("sala_id"):
        valores = [request.form["sala_id"]]

    try:
        return list(dict.fromkeys(int(valor) for valor in valores if valor))
    except ValueError:
        return []


def _validar_evento(datos, ids_salas, evento_id=None, exigir_fecha_futura=False):
    errores = []
    campos_requeridos = (
        "responsable", "nombre_evento", "asistentes", "fecha",
        "hora_inicio", "hora_fin", "tipo_acomodo",
    )
    if any(datos.get(campo) in (None, "") for campo in campos_requeridos):
        errores.append("Completa todos los datos obligatorios del evento.")
        return errores, []

    if datos["asistentes"] < 1:
        errores.append("La cantidad de asistentes debe ser mayor que cero.")
    if datos["hora_fin"] <= datos["hora_inicio"]:
        errores.append("La hora de fin debe ser posterior a la hora de inicio.")
    if exigir_fecha_futura and datos["fecha"] < date.today():
        errores.append("No se puede registrar un evento en una fecha pasada.")
    if not 1 <= len(ids_salas) <= 2:
        errores.append("Selecciona una sala, o dos cuando la capacidad lo requiera.")

    salas = Sala.query.filter(Sala.id.in_(ids_salas)).all() if ids_salas else []
    if len(salas) != len(ids_salas):
        errores.append("Una de las salas seleccionadas no existe.")
        return errores, salas

    if salas:
        mayor_capacidad = max(sala.capacidad for sala in salas)
        capacidad_total = sum(sala.capacidad for sala in salas)
        if datos["asistentes"] > capacidad_total and len(salas) < 2:
            errores.append("Para este número de asistentes debes seleccionar dos salas.")
        elif datos["asistentes"] > capacidad_total:
            errores.append(
                f"Las salas seleccionadas admiten {capacidad_total} asistentes como máximo."
            )
        elif datos["asistentes"] > mayor_capacidad and len(salas) < 2:
            errores.append("Para este número de asistentes debes seleccionar dos salas.")

    if not errores and salas:
        conflicto = Evento.query.filter(
            Evento.fecha == datos["fecha"],
            Evento.estado != "Cancelado",
            Evento.hora_inicio < datos["hora_fin"],
            Evento.hora_fin > datos["hora_inicio"],
            or_(
                Evento.sala_id.in_(ids_salas),
                Evento.salas.any(Sala.id.in_(ids_salas)),
            ),
        )
        if evento_id is not None:
            conflicto = conflicto.filter(Evento.id != evento_id)
        if conflicto.first():
            errores.append("Una de las salas ya está reservada en ese horario.")

    return errores, salas


def _contexto_form(datos=None, ids_salas=None, **extra):
    contexto = dict(extra)
    if datos:
        contexto.update(datos)
    contexto["sala_ids"] = ids_salas or []
    return contexto


@eventos_bp.route("/registrar", methods=["GET", "POST"])
def registrar():
    salas = Sala.query.all()  # para el selector de sala

    if request.method == "POST":
        try:
            datos = _datos_form()
        except (TypeError, ValueError):
            flash("La fecha o el horario no tienen un formato válido.", "danger")
            return render_template(
                "registrar_evento.html", salas=salas,
                sala_ids=_ids_salas_form(), form=request.form,
            ), 400

        ids_salas = _ids_salas_form()
        errores, salas_seleccionadas = _validar_evento(
            datos, ids_salas, exigir_fecha_futura=True
        )
        if errores:
            for error in errores:
                flash(error, "danger")
            return render_template(
                "registrar_evento.html", salas=salas,
                **_contexto_form(datos, ids_salas)
            ), 400

        nuevo_evento = Evento(
            estado="Activo",
            sala_id=ids_salas[0],
            salas=salas_seleccionadas,
            **datos,
        )

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
    evento = db.get_or_404(Evento, id)
    salas = Sala.query.all()

    if request.method == "POST":
        try:
            datos = _datos_form()
        except (TypeError, ValueError):
            flash("La fecha o el horario no tienen un formato válido.", "danger")
            return render_template(
                "registrar_evento.html", salas=salas, evento=evento,
                editando=True, sala_ids=_ids_salas_form(),
            ), 400

        ids_salas = _ids_salas_form()
        errores, salas_seleccionadas = _validar_evento(
            datos, ids_salas, evento_id=evento.id
        )
        if errores:
            for error in errores:
                flash(error, "danger")
            return render_template(
                "registrar_evento.html", salas=salas, evento=evento,
                **_contexto_form(datos, ids_salas, editando=True)
            ), 400

        # Detectamos qué campos cambiaron para describir la modificación
        cambios = [
            campo
            for campo, valor in datos.items()
            if getattr(evento, campo) != valor
        ]
        ids_salas_actuales = {sala.id for sala in evento.salas_asignadas}
        if ids_salas_actuales != set(ids_salas):
            cambios.append("salas")

        for campo, valor in datos.items():
            setattr(evento, campo, valor)
        evento.sala_id = ids_salas[0]
        evento.salas = salas_seleccionadas

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
        sala_ids=[sala.id for sala in evento.salas_asignadas],
        extension=evento.extension,
        cafeteria=evento.cafeteria,
        sonido=evento.sonido,
        videoconferencia=evento.videoconferencia,
    )


@eventos_bp.route("/cancelar/<int:id>", methods=["POST"])
def cancelar(id):
    evento = db.get_or_404(Evento, id)
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
