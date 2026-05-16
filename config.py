import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "chave-dev-taskflow"

    uri = os.environ.get("DATABASE_URL") or "sqlite:///taskflow.db"

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False