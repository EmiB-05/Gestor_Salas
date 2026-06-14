from flask import Flask
from config import Config
from database.db import db
import os

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

from routes.eventos import eventos_bp

app.register_blueprint(eventos_bp)

if __name__ == "__main__":

    print(os.getenv("DB_NAME"))

    with app.app_context():
        db.create_all()

    app.run(debug=True)