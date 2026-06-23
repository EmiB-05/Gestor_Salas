# routes/reporte.py
from datetime import date, timedelta
from io import BytesIO

from flask import Blueprint, request, send_file, jsonify

from modelos.sala import Sala
from modelos.evento import Evento
from utils.pdf_reporte import generar_reporte_semanal

reporte_bp = Blueprint("reporte", __name__, url_prefix="/reporte")


def _lunes_de(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _construir_datos(inicio: date, fin: date):
    """Consulta SQLAlchemy y devuelve (salas, eventos_por_sala) para el PDF."""

    # ── Salas ─────────────────────────────────────────────────────────────────
    todas_las_salas = Sala.query.order_by(Sala.nombre).all()

    # Eventos activos de la semana agrupados por sala
    eventos_semana = (
        Evento.query
        .filter(Evento.fecha >= inicio, Evento.fecha <= fin)
        .order_by(Evento.fecha, Evento.hora_inicio)
        .all()
    )

    # Conteo de eventos por sala_id (sala principal)
    conteo = {}
    for ev in eventos_semana:
        for sala in ev.salas_asignadas:
            conteo[sala.id] = conteo.get(sala.id, 0) + 1

    salas_data = []
    for sala in todas_las_salas:
        salas_data.append({
            "nombre":        sala.nombre,
            "capacidad":     sala.capacidad,
            "total_eventos": conteo.get(sala.id, 0),
            "servicios":     ["Cafetería", "Sonido", "Videoconferencia", "Extensiones"],
        })

    # ── Eventos por sala ───────────────────────────────────────────────────────
    eventos_por_sala = {sala.nombre: [] for sala in todas_las_salas}

    for ev in eventos_semana:
        servicios_activos = []
        if ev.cafeteria:        servicios_activos.append("Cafetería")
        if ev.sonido:           servicios_activos.append("Sonido")
        if ev.videoconferencia: servicios_activos.append("Videoconferencia")
        if ev.extension:        servicios_activos.append("Extensiones")

        ev_dict = {
            "nombre_evento": ev.nombre_evento,
            "responsable":   ev.responsable,
            "fecha":         ev.fecha,
            "hora_inicio":   str(ev.hora_inicio)[:5],
            "hora_fin":      str(ev.hora_fin)[:5],
            "asistentes":    ev.asistentes,
            "tipo_acomodo":  ev.tipo_acomodo or "—",
            "estado":        ev.estado,
            "servicios":     servicios_activos,
        }

        # El evento aparece bajo cada sala que ocupa
        nombres_vistos = set()
        for sala in ev.salas_asignadas:
            if sala.nombre in eventos_por_sala and sala.nombre not in nombres_vistos:
                eventos_por_sala[sala.nombre].append(ev_dict)
                nombres_vistos.add(sala.nombre)

    return salas_data, eventos_por_sala


@reporte_bp.route("/semanal")
def reporte_semanal():
    """
    GET /reporte/semanal              → semana actual
    GET /reporte/semanal?fecha=2025-06-16 → semana que contiene esa fecha
    """
    fecha_param = request.args.get("fecha")
    try:
        dia_ref = date.fromisoformat(fecha_param) if fecha_param else date.today()
    except ValueError:
        return jsonify({"error": "Formato inválido. Usa YYYY-MM-DD."}), 400

    inicio = _lunes_de(dia_ref)
    fin    = inicio + timedelta(days=6)

    salas_data, eventos_por_sala = _construir_datos(inicio, fin)
    pdf_bytes = generar_reporte_semanal(salas_data, eventos_por_sala, inicio)

    nombre_archivo = f"reporte_salas_{inicio.strftime('%Y-%m-%d')}.pdf"
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=nombre_archivo,
    )