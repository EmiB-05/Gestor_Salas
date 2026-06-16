from flask import Flask
from config import Config
from database.db import db
import os
from routes.calendario import calendar_bp
from routes.eventos import eventos_bp
from modelos.evento import Evento
from modelos.sala import Sala

app = Flask(__name__)

app.config.from_object(Config)
app.register_blueprint(calendar_bp)
app.register_blueprint(eventos_bp)

db.init_app(app)

if __name__ == "__main__":

    print(os.getenv("DB_NAME"))

    with app.app_context():
        db.create_all()

    app.run(debug=True)