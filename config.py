# Configurações gerais
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "chave-dev-taskflow"

    SQLALCHEMY_DATABASE_URI = "sqlite:///taskflow.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False