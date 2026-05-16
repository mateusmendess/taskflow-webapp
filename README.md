# ✅ TaskFlow

> Aplicação web de gerenciamento de tarefas com autenticação, filtros dinâmicos, ordenação em tempo real e dashboard responsivo.

[![Deploy](https://img.shields.io/badge/deploy-railway-6366f1?style=for-the-badge&logo=railway)](https://taskflow-webapp-production.up.railway.app)
[![Python](https://img.shields.io/badge/Python-3.x-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-cc2927?style=for-the-badge)](https://sqlalchemy.org)

---

## 🌐 Demo

**Acesse o projeto online:** [taskflow-webapp-production.up.railway.app](https://taskflow-webapp-production.up.railway.app)

---

## 📸 Screenshots

> _Em breve: screenshots e GIF do dashboard_

---

## 🚀 Funcionalidades

### Autenticação
- Cadastro e login de usuários
- Logout seguro
- Proteção de rotas com Flask-Login

### Tarefas
- Criar, editar e excluir tarefas
- Campos: título, descrição, prioridade, status e data de vencimento
- Concluir tarefa sem recarregar a página (fetch API)

### Dashboard
- Cards de estatísticas: Total, Pendentes, Concluídas e Atrasadas
- Indicadores visuais por cor: atrasadas, vencendo hoje e concluídas

### Filtros dinâmicos (sem reload)
- Por status: Todas, Pendentes, Concluídas
- Por prioridade: Alta, Média, Baixa
- Por vencimento: Atrasadas, Hoje, Futuras, Sem data

### Pesquisa e ordenação
- Pesquisa em tempo real por título e descrição
- Ordenação por: mais importantes, vencimento, prioridade, mais recentes e mais antigas

---

## 🛠️ Tecnologias

| Camada | Tecnologia |
|---|---|
| Backend | Python, Flask |
| Banco de dados | SQLite (local) / PostgreSQL (produção) |
| ORM | SQLAlchemy, Flask-SQLAlchemy |
| Autenticação | Flask-Login, Flask-Bcrypt |
| Frontend | HTML5, CSS3, JavaScript |
| Deploy | Railway |

---

## 📁 Estrutura do projeto

```
taskflow-webapp/
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models.py
│   ├── routes.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── script.js
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── login.html
│       ├── register.html
│       └── edit_task.html
├── config.py
├── run.py
├── requirements.txt
└── Procfile
```

---

## ⚙️ Como rodar localmente

### Pré-requisitos
- Python 3.10+
- pip

### Passo a passo

**1. Clone o repositório**
```bash
git clone https://github.com/mateusmendess/taskflow-webapp.git
cd taskflow-webapp
```

**2. Crie e ative o ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:
```
SECRET_KEY=sua-chave-secreta-aqui
```

**5. Rode o projeto**
```bash
python run.py
```

**6. Acesse no navegador**
```
http://localhost:5000
```

---

## 🔮 Próximas melhorias

- Responsividade mobile avançada
- Dark mode
- Sistema Kanban
- Analytics de produtividade
- Upload de arquivos

---

## 👨‍💻 Autor

Feito por **Mateus Mendes**

[![GitHub](https://img.shields.io/badge/GitHub-mateusmendess-181717?style=for-the-badge&logo=github)](https://github.com/mateusmendess)

---

## 📄 Licença

Este projeto está sob a licença MIT.