from flask import Flask
from datetime import timedelta
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)  # Nécessaire pour la session
    app.permanent_session_lifetime = timedelta(minutes=30)
    from .routes import main
    app.register_blueprint(main)

    return app
