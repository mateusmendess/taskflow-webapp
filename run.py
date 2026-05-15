# Arquivo principal para rodar o projeto
from dotenv import load_dotenv
from app import create_app
from app.extensions import db

load_dotenv()

app = create_app()

from app.models import User, Task

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)