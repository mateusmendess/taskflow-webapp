from flask import Flask
from config import Config
from .extensions import db, bcrypt, login_manager, mail

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app