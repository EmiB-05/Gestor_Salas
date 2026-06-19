import unittest
from datetime import date, timedelta

from flask import Flask

from database.db import db
from modelos.evento import Evento
from modelos.historial import Historial
from modelos.sala import Sala
from routes.calendario import calendar_bp
from routes.estadisticas import estadisticas_bp
from routes.eventos import eventos_bp
from routes.historial import historial_bp


class EventosTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__, template_folder="../templates", static_folder="../static")
        self.app.config.update(
            TESTING=True,
            SECRET_KEY="test",
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        self.app.register_blueprint(calendar_bp)
        self.app.register_blueprint(eventos_bp)
        self.app.register_blueprint(estadisticas_bp)
        self.app.register_blueprint(historial_bp)
        db.init_app(self.app)

        with self.app.app_context():
            db.create_all()
            db.session.add_all([
                Sala(nombre="Sala A", capacidad=40),
                Sala(nombre="Sala B", capacidad=40),
                Sala(nombre="Sala C", capacidad=40),
            ])
            db.session.commit()

        self.client = self.app.test_client()
        self.fecha = (date.today() + timedelta(days=1)).isoformat()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def datos(self, **cambios):
        datos = {
            "responsable": "Emilio",
            "nombre_evento": "Taller",
            "asistentes": "30",
            "fecha": self.fecha,
            "hora_inicio": "10:00",
            "hora_fin": "11:00",
            "tipo_acomodo": "Aula",
            "sala_ids": "1",
        }
        datos.update(cambios)
        return datos

    def test_rechaza_evento_incompleto_que_romperia_el_calendario(self):
        respuesta = self.client.post("/registrar", data=self.datos(hora_fin=""))

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn(b"Completa todos los datos obligatorios", respuesta.data)
        with self.app.app_context():
            self.assertEqual(Evento.query.count(), 0)

    def test_mas_de_40_asistentes_requiere_dos_salas(self):
        respuesta = self.client.post("/registrar", data=self.datos(asistentes="60"))

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn(b"debes seleccionar dos salas", respuesta.data)

    def test_registra_dos_salas_y_muestra_detalles_del_nuevo_evento(self):
        datos = self.datos(asistentes="60")
        datos["sala_ids"] = ["1", "2"]
        respuesta = self.client.post("/registrar", data=datos)

        self.assertEqual(respuesta.status_code, 302)
        with self.app.app_context():
            evento = Evento.query.one()
            self.assertEqual([sala.nombre for sala in evento.salas_asignadas], ["Sala A", "Sala B"])
            self.assertEqual(Historial.query.count(), 1)

        calendario = self.client.get("/")
        self.assertEqual(calendario.status_code, 200)
        self.assertIn(b"Sala A, Sala B", calendario.data)
        self.assertIn(b"Sin hora de fin", calendario.data)

        historial = self.client.get("/historial")
        self.assertIn(b"Sala A, Sala B", historial.data)
        with self.app.app_context():
            movimiento_id = Historial.query.one().id
        detalle = self.client.get(f"/historial/{movimiento_id}")
        self.assertIn(b"Sala A, Sala B", detalle.data)

        estadisticas = self.client.get("/estadisticas")
        self.assertEqual(estadisticas.status_code, 200)

    def test_rechaza_traslape_en_cualquiera_de_las_salas(self):
        primero = self.datos(asistentes="60")
        primero["sala_ids"] = ["1", "2"]
        self.assertEqual(self.client.post("/registrar", data=primero).status_code, 302)

        segundo = self.datos(
            nombre_evento="Otro evento",
            hora_inicio="10:30",
            hora_fin="12:00",
            sala_ids="2",
        )
        respuesta = self.client.post("/registrar", data=segundo)

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn(b"ya est\xc3\xa1 reservada", respuesta.data)
        with self.app.app_context():
            self.assertEqual(Evento.query.count(), 1)

    def test_rechaza_horario_invertido(self):
        respuesta = self.client.post(
            "/registrar", data=self.datos(hora_inicio="12:00", hora_fin="11:00")
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn(b"hora de fin debe ser posterior", respuesta.data)


if __name__ == "__main__":
    unittest.main()
