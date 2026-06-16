from database.db import db

class Evento(db.Model):

    __tablename__ = "eventos"

    id = db.Column(db.Integer, primary_key=True)

    responsable = db.Column(db.String(100))

    nombre_evento = db.Column(db.String(150))

    asistentes = db.Column(db.Integer)

    fecha = db.Column(db.Date)

    hora_inicio = db.Column(db.Time)

    hora_fin = db.Column(db.Time)

    tipo_acomodo = db.Column(db.String(50))

    estado = db.Column(db.String(20))

    sala_id = db.Column(
        db.Integer,
        db.ForeignKey("salas.id")
    )

    sala = db.relationship("Sala")