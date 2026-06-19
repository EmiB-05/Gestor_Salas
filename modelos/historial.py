# historial.py
from datetime import datetime, timezone
from database.db import db


class Historial(db.Model):
    __tablename__ = "historial"

    id             = db.Column(db.Integer, primary_key=True)
    evento_id      = db.Column(db.Integer, db.ForeignKey("eventos.id"))
    accion         = db.Column(db.String(20))   # Original / Modificado / Cancelado
    descripcion    = db.Column(db.String(255))
    fecha_registro = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    evento = db.relationship("Evento")
