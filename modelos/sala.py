from database.db import db

class Sala(db.Model):
    __tablename__ = "salas"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    capacidad = db.Column(db.Integer)