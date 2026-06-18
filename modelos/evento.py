# evento.py
from database.db import db

class Evento(db.Model):
    __tablename__ = "eventos"

    id             = db.Column(db.Integer, primary_key=True)
    responsable    = db.Column(db.String(100))
    nombre_evento  = db.Column(db.String(150))
    asistentes     = db.Column(db.Integer)
    fecha          = db.Column(db.Date)
    hora_inicio    = db.Column(db.Time)
    hora_fin       = db.Column(db.Time)
    tipo_acomodo   = db.Column(db.String(50))
    estado         = db.Column(db.String(20), default="pendiente")

    # Extras
    extension        = db.Column(db.Boolean, default=False)
    cafeteria        = db.Column(db.Boolean, default=False)
    sonido           = db.Column(db.Boolean, default=False)
    videoconferencia = db.Column(db.Boolean, default=False)

    sala_id = db.Column(db.Integer, db.ForeignKey("salas.id"))
    sala    = db.relationship("Sala")