"""
pdf_reporte.py
Genera un reporte semanal en PDF de salas y eventos.
Uso en Flask:
    from pdf_reporte import generar_reporte_semanal
"""

from io import BytesIO
from datetime import date, timedelta

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# ── Paleta de colores ──────────────────────────────────────────────────────────
AZUL_OSCURO  = colors.HexColor("#1E3A5F")
AZUL_MEDIO   = colors.HexColor("#2E6DA4")
AZUL_CLARO   = colors.HexColor("#D6E8FA")
GRIS_LINEA   = colors.HexColor("#CBD5E0")
GRIS_FONDO   = colors.HexColor("#F7FAFC")
VERDE        = colors.HexColor("#276749")
ROJO         = colors.HexColor("#9B2335")
BLANCO       = colors.white


def _estilos():
    base = getSampleStyleSheet()
    extra = {
        "Titulo": ParagraphStyle(
            "Titulo", parent=base["Title"],
            fontSize=20, textColor=BLANCO, alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "Subtitulo": ParagraphStyle(
            "Subtitulo", parent=base["Normal"],
            fontSize=10, textColor=BLANCO, alignment=TA_CENTER,
        ),
        "SeccionHeader": ParagraphStyle(
            "SeccionHeader", parent=base["Heading2"],
            fontSize=13, textColor=AZUL_OSCURO,
            spaceBefore=14, spaceAfter=4,
        ),
        "SalaHeader": ParagraphStyle(
            "SalaHeader", parent=base["Normal"],
            fontSize=11, textColor=BLANCO,
            spaceBefore=0, spaceAfter=0,
        ),
        "Normal": base["Normal"],
        "Small": ParagraphStyle(
            "Small", parent=base["Normal"],
            fontSize=8, textColor=colors.HexColor("#4A5568"),
        ),
        "Celda": ParagraphStyle(
            "Celda", parent=base["Normal"],
            fontSize=8, leading=10,
        ),
    }
    return {**{k: base[k] for k in base.byName}, **extra}


def _semana_labels(inicio: date):
    dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    return [
        f"{dias[i]}\n{(inicio + timedelta(days=i)).strftime('%d/%m')}"
        for i in range(7)
    ]


def _tabla_estilo_base():
    return [
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0),  8),
        ("BACKGROUND",  (0, 0), (-1, 0),  AZUL_MEDIO),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  BLANCO),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME",    (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",    (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANCO, GRIS_FONDO]),
        ("GRID",        (0, 0), (-1, -1), 0.4, GRIS_LINEA),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]


# ── Sección 1: Resumen de Salas ────────────────────────────────────────────────
def _seccion_salas(salas: list[dict], s) -> list:
    """
    salas: [{"nombre": str, "capacidad": int, "total_eventos": int, "servicios": [str]}]
    """
    story = []
    story.append(Paragraph("Resumen de Salas", s["SeccionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=AZUL_MEDIO, spaceAfter=8))

    cabecera = [["Sala", "Capacidad", "Eventos\nen la semana", "Servicios disponibles"]]
    filas = []
    for sala in salas:
        servicios_str = ", ".join(sala.get("servicios", [])) or "—"
        filas.append([
            Paragraph(f"<b>{sala['nombre']}</b>", s["Celda"]),
            str(sala["capacidad"]),
            str(sala.get("total_eventos", 0)),
            Paragraph(servicios_str, s["Celda"]),
        ])

    tabla = Table(
        cabecera + filas,
        colWidths=[3.8 * cm, 2.8 * cm, 3.2 * cm, 8.2 * cm],
    )
    estilo = _tabla_estilo_base() + [
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("ALIGN", (3, 1), (3, -1), "LEFT"),
    ]
    tabla.setStyle(TableStyle(estilo))
    story.append(tabla)
    return story


# ── Sección 2: Eventos por sala ────────────────────────────────────────────────
def _seccion_eventos_por_sala(eventos_por_sala: dict[str, list], inicio: date, s) -> list:
    """
    eventos_por_sala: {
        "Sala A": [
            {
                "nombre_evento": str, "responsable": str,
                "fecha": date, "hora_inicio": str, "hora_fin": str,
                "asistentes": int, "tipo_acomodo": str,
                "estado": str,
                "servicios": [str],   # lista de servicios activos
            }
        ]
    }
    """
    story = []
    story.append(Paragraph("Eventos por Sala", s["SeccionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=AZUL_MEDIO, spaceAfter=8))

    if not eventos_por_sala:
        story.append(Paragraph("No hay eventos registrados esta semana.", s["Normal"]))
        return story

    for nombre_sala, eventos in eventos_por_sala.items():
        # Header de sala
        header_tabla = Table(
            [[Paragraph(f"  {nombre_sala}", s["SalaHeader"])]],
            colWidths=[18 * cm],
        )
        header_tabla.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), AZUL_OSCURO),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ]))
        story.append(header_tabla)

        if not eventos:
            sin_eventos = Table(
                [["Sin eventos esta semana"]],
                colWidths=[18 * cm],
            )
            sin_eventos.setStyle(TableStyle([
                ("FONTNAME",  (0, 0), (-1, -1), "Helvetica-Oblique"),
                ("FONTSIZE",  (0, 0), (-1, -1), 8),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.grey),
                ("TOPPADDING",    (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING",   (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.3, GRIS_LINEA),
            ]))
            story.append(sin_eventos)
            story.append(Spacer(1, 8))
            continue

        cabecera = [[
            "Evento", "Responsable", "Fecha", "Horario",
            "Asistentes", "Acomodo", "Servicios", "Estado"
        ]]
        filas = []
        for ev in eventos:
            fecha_str = ev["fecha"].strftime("%d/%m/%Y") if hasattr(ev["fecha"], "strftime") else str(ev["fecha"])
            servicios_str = Paragraph(", ".join(ev.get("servicios", [])) or "—", s["Celda"])
            estado = ev.get("estado", "Activo")
            estado_color = VERDE if estado == "Activo" else (ROJO if estado == "Cancelado" else colors.orange)

            filas.append([
                Paragraph(f"<b>{ev['nombre_evento']}</b>", s["Celda"]),
                Paragraph(ev["responsable"], s["Celda"]),
                fecha_str,
                f"{ev['hora_inicio']} -\n{ev['hora_fin']}",
                str(ev["asistentes"]),
                Paragraph(ev.get("tipo_acomodo", "—"), s["Celda"]),
                servicios_str,
                Paragraph(f"<font color='#{estado_color.hexval()[2:]}'><b>{estado}</b></font>", s["Celda"]),
            ])

        tabla = Table(
            cabecera + filas,
            colWidths=[3.5 * cm, 3 * cm, 1.8 * cm, 1.8 * cm, 1.5 * cm, 2 * cm, 2.8 * cm, 1.6 * cm],
        )
        estilo = _tabla_estilo_base() + [
            ("ALIGN", (0, 1), (1, -1), "LEFT"),
            ("ALIGN", (6, 1), (6, -1), "LEFT"),
        ]
        tabla.setStyle(TableStyle(estilo))
        story.append(tabla)
        story.append(Spacer(1, 10))

    return story


# ── Sección 3: Vista semanal (calendario) ─────────────────────────────────────
def _seccion_calendario(eventos_por_sala: dict[str, list], inicio: date, s) -> list:
    """Vista de cuadrícula: filas = salas, columnas = días de la semana."""
    story = []
    story.append(Paragraph("Vista Semanal", s["SeccionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=AZUL_MEDIO, spaceAfter=8))

    dias_labels = _semana_labels(inicio)
    cabecera = [["Sala"] + dias_labels]
    filas = []

    for nombre_sala, eventos in eventos_por_sala.items():
        fila = [Paragraph(f"<b>{nombre_sala}</b>", s["Celda"])]
        for i in range(7):
            dia = inicio + timedelta(days=i)
            evs_del_dia = [ev for ev in eventos if ev["fecha"] == dia]
            if evs_del_dia:
                textos = []
                for ev in evs_del_dia:
                    textos.append(
                        f"<b>{ev['hora_inicio'][:5]}</b> {ev['nombre_evento'][:18]}"
                    )
                celda = Paragraph("<br/>".join(textos), s["Celda"])
            else:
                celda = Paragraph("<font color='#A0AEC0'>—</font>", s["Celda"])
            fila.append(celda)
        filas.append(fila)

    col_sala  = 3.2 * cm
    col_dia   = (18 * cm - col_sala) / 7
    tabla = Table(
        cabecera + filas,
        colWidths=[col_sala] + [col_dia] * 7,
        rowHeights=None,
    )
    estilo = _tabla_estilo_base() + [
        ("ALIGN",  (0, 1), (0, -1), "LEFT"),
        ("ALIGN",  (1, 1), (-1, -1), "LEFT"),
        ("FONTSIZE", (0, 0), (-1, 0), 7),
        ("FONTSIZE", (0, 1), (-1, -1), 7),
    ]
    tabla.setStyle(TableStyle(estilo))
    story.append(tabla)
    return story


# ── Cabecera con fondo azul ────────────────────────────────────────────────────
def _header_pdf(canvas_obj, doc, titulo: str, rango: str):
    canvas_obj.saveState()
    w, h = letter
    rect_h = 2.8 * cm
    canvas_obj.setFillColor(AZUL_OSCURO)
    canvas_obj.rect(0, h - rect_h, w, rect_h, fill=True, stroke=False)

    canvas_obj.setFillColor(BLANCO)
    canvas_obj.setFont("Helvetica-Bold", 16)
    canvas_obj.drawCentredString(w / 2, h - 1.4 * cm, titulo)
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.drawCentredString(w / 2, h - 2 * cm, rango)

    # Pie de página
    canvas_obj.setFillColor(GRIS_LINEA)
    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.drawCentredString(w / 2, 0.6 * cm, f"Página {doc.page}")
    canvas_obj.restoreState()


# ── Función principal ──────────────────────────────────────────────────────────
def generar_reporte_semanal(
    salas: list[dict],
    eventos_por_sala: dict[str, list],
    inicio_semana: date | None = None,
) -> bytes:
    """
    Genera el PDF y devuelve los bytes listos para enviar con Flask send_file.

    Parámetros
    ----------
    salas : lista de dicts con keys: nombre, capacidad, total_eventos, servicios
    eventos_por_sala : dict {nombre_sala: [lista de eventos]}
        Cada evento: nombre_evento, responsable, fecha (date), hora_inicio (str HH:MM),
                     hora_fin (str HH:MM), asistentes, tipo_acomodo, estado, servicios (list[str])
    inicio_semana : date del lunes; si es None usa el lunes de la semana actual
    """
    if inicio_semana is None:
        hoy = date.today()
        inicio_semana = hoy - timedelta(days=hoy.weekday())

    fin_semana = inicio_semana + timedelta(days=6)
    rango_str = (
        f"Semana del {inicio_semana.strftime('%d de %B')} "
        f"al {fin_semana.strftime('%d de %B de %Y')}"
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=3.2 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
    )

    s = _estilos()
    story = []
    story.append(Spacer(1, 0.4 * cm))

    story += _seccion_salas(salas, s)
    story.append(Spacer(1, 0.5 * cm))
    story += _seccion_eventos_por_sala(eventos_por_sala, inicio_semana, s)
    story.append(Spacer(1, 0.5 * cm))
    story += _seccion_calendario(eventos_por_sala, inicio_semana, s)

    doc.build(
        story,
        onFirstPage=lambda c, d: _header_pdf(c, d, "Reporte Semanal de Salas", rango_str),
        onLaterPages=lambda c, d: _header_pdf(c, d, "Reporte Semanal de Salas", rango_str),
    )

    buffer.seek(0)
    return buffer.read()