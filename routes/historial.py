from flask import Blueprint, render_template
from modelos.evento import Evento
from modelos.historial import Historial

historial_bp = Blueprint(
    "historial",
    __name__
)


@historial_bp.route("/historial")
def historial():

    movimientos = (
        Historial.query
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
                evento.sala.nombre
                if evento and evento.sala else "Sin asignar"
            ),
            "evento": evento.nombre_evento if evento else "Evento eliminado",
            "estado": mov.accion,
        })

    # --- Métricas reales ---
    total_movimientos = Historial.query.count()
    modificaciones = Historial.query.filter_by(accion="Modificado").count()

    total_eventos = Evento.query.count()
    cancelados = Evento.query.filter_by(estado="Cancelado").count()
    vigentes = total_eventos - cancelados
    cumplimiento = round(vigentes / total_eventos * 100) if total_eventos else 0

    return render_template(
        "historial.html",
        registros=registros,
        frecuencia_cambio=modificaciones,
        cumplimiento=f"{cumplimiento}%",
        optimizacion=total_movimientos,
    )


@historial_bp.route("/historial/<int:id>")
def detalle(id):
    mov = Historial.query.get_or_404(id)
    return render_template("historial_detalle.html", movimiento=mov)
