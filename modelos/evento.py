# evento.py
from database.db import db

evento_salas = db.Table(
    "evento_salas",
    db.Column("evento_id", db.Integer, db.ForeignKey("eventos.id"), primary_key=True),
    db.Column("sala_id", db.Integer, db.ForeignKey("salas.id"), primary_key=True),
)


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

    # sala_id se conserva como sala principal para compatibilidad con los datos
    # existentes. La tabla evento_salas permite reservar una segunda sala.
    sala_id = db.Column(db.Integer, db.ForeignKey("salas.id"))
    sala = db.relationship("Sala", foreign_keys=[sala_id])
    salas = db.relationship("Sala", secondary=evento_salas, lazy="selectin")

    @property
    def salas_asignadas(self):
        """Devuelve también la sala principal de registros anteriores."""
        salas = list(self.salas)
        if self.sala and self.sala not in salas:
            salas.insert(0, self.sala)
        return salas
