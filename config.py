import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "chave-dev-taskflow"

    uri = os.environ.get("DATABASE_URL") or "sqlite:///taskflow.db"

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql+pg8000://", 1)

    elif uri.startswith("postgresql://"):
        uri = uri.replace("postgresql://", "postgresql+pg8000://", 1)

    SQLALCHEMY_DATABASE_URI = uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False

   # Flask-Mail
    MAIL_SERVER   = "smtp.gmail.com"
    MAIL_PORT     = 465
    MAIL_USE_SSL  = True
    MAIL_USE_TLS  = False
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = ("TaskFlow", os.environ.get("MAIL_USERNAME"))