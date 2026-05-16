from flask import render_template_string
from flask_mail import Message
from datetime import date
from .extensions import mail
from .models import User, Task


EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TaskFlow</title>
</head>
<body style="margin:0; padding:0; background:#f4f6f8; font-family: Arial, sans-serif;">

    <div style="max-width:580px; margin:32px auto; background:#ffffff; border-radius:16px; overflow:hidden; border:1px solid #e5e7eb;">

        <!-- Header -->
        <div style="background:#2563eb; padding:28px 32px; text-align:center;">
            <div style="display:inline-flex; align-items:center; gap:10px;">
                <div style="width:32px; height:32px; background:rgba(255,255,255,0.2); border-radius:8px; display:inline-flex; align-items:center; justify-content:center; font-size:1rem;">✓</div>
                <span style="color:#ffffff; font-size:1.3rem; font-weight:800; letter-spacing:-0.3px;">TaskFlow</span>
            </div>
            <p style="color:rgba(255,255,255,0.85); margin:10px 0 0; font-size:0.92rem;">Resumo diário de tarefas</p>
        </div>

        <!-- Body -->
        <div style="padding:32px;">

            <p style="font-size:1rem; color:#111827; margin:0 0 24px;">
                Olá, <strong>{{ name }}</strong>! 👋 Aqui está o resumo das suas tarefas para hoje.
            </p>

            {% if today_tasks %}
            <div style="margin-bottom:24px;">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                    <span style="font-size:1rem;">📅</span>
                    <h2 style="font-size:0.95rem; font-weight:800; color:#111827; margin:0; text-transform:uppercase; letter-spacing:0.5px;">Vencem hoje</h2>
                </div>
                {% for task in today_tasks %}
                <div style="background:#fffbeb; border:1.5px solid #fde68a; border-radius:10px; padding:14px 16px; margin-bottom:8px;">
                    <div style="font-size:0.92rem; font-weight:700; color:#111827; margin-bottom:6px;">{{ task.title }}</div>
                    {% if task.description %}
                    <div style="font-size:0.82rem; color:#6b7280; margin-bottom:8px;">{{ task.description[:80] }}{% if task.description|length > 80 %}...{% endif %}</div>
                    {% endif %}
                    <span style="display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700;
                        {% if task.priority == 'alta' %}background:#fff5f5; color:#dc2626;
                        {% elif task.priority == 'media' %}background:#fffaf0; color:#d97706;
                        {% else %}background:#eff6ff; color:#2563eb;{% endif %}">
                        {% if task.priority == 'alta' %}🔥 Alta
                        {% elif task.priority == 'media' %}⚡ Média
                        {% else %}🌱 Baixa{% endif %}
                    </span>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% if tomorrow_tasks %}
            <div style="margin-bottom:24px;">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                    <span style="font-size:1rem;">➡️</span>
                    <h2 style="font-size:0.95rem; font-weight:800; color:#111827; margin:0; text-transform:uppercase; letter-spacing:0.5px;">Vencem amanhã</h2>
                </div>
                {% for task in tomorrow_tasks %}
                <div style="background:#eff6ff; border:1.5px solid #bfdbfe; border-radius:10px; padding:14px 16px; margin-bottom:8px;">
                    <div style="font-size:0.92rem; font-weight:700; color:#111827; margin-bottom:6px;">{{ task.title }}</div>
                    {% if task.description %}
                    <div style="font-size:0.82rem; color:#6b7280; margin-bottom:8px;">{{ task.description[:80] }}{% if task.description|length > 80 %}...{% endif %}</div>
                    {% endif %}
                    <span style="display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700;
                        {% if task.priority == 'alta' %}background:#fff5f5; color:#dc2626;
                        {% elif task.priority == 'media' %}background:#fffaf0; color:#d97706;
                        {% else %}background:#eff6ff; color:#2563eb;{% endif %}">
                        {% if task.priority == 'alta' %}🔥 Alta
                        {% elif task.priority == 'media' %}⚡ Média
                        {% else %}🌱 Baixa{% endif %}
                    </span>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% if overdue_tasks %}
            <div style="margin-bottom:24px;">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                    <span style="font-size:1rem;">⚠️</span>
                    <h2 style="font-size:0.95rem; font-weight:800; color:#dc2626; margin:0; text-transform:uppercase; letter-spacing:0.5px;">Atrasadas</h2>
                </div>
                {% for task in overdue_tasks %}
                <div style="background:#fff1f2; border:1.5px solid #fca5a5; border-radius:10px; padding:14px 16px; margin-bottom:8px;">
                    <div style="font-size:0.92rem; font-weight:700; color:#111827; margin-bottom:6px;">{{ task.title }}</div>
                    <div style="font-size:0.78rem; color:#dc2626; font-weight:600; margin-bottom:6px;">
                        Venceu em {{ task.due_date.strftime("%d/%m/%Y") }}
                    </div>
                    {% if task.description %}
                    <div style="font-size:0.82rem; color:#6b7280; margin-bottom:8px;">{{ task.description[:80] }}{% if task.description|length > 80 %}...{% endif %}</div>
                    {% endif %}
                    <span style="display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700;
                        {% if task.priority == 'alta' %}background:#fff5f5; color:#dc2626;
                        {% elif task.priority == 'media' %}background:#fffaf0; color:#d97706;
                        {% else %}background:#eff6ff; color:#2563eb;{% endif %}">
                        {% if task.priority == 'alta' %}🔥 Alta
                        {% elif task.priority == 'media' %}⚡ Média
                        {% else %}🌱 Baixa{% endif %}
                    </span>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% if not today_tasks and not tomorrow_tasks and not overdue_tasks %}
            <div style="text-align:center; padding:32px; background:#f0fdf4; border-radius:12px; margin-bottom:24px;">
                <div style="font-size:2rem; margin-bottom:8px;">🎉</div>
                <p style="font-size:0.92rem; font-weight:700; color:#16a34a; margin:0;">Tudo em dia! Nenhuma tarefa pendente ou atrasada.</p>
            </div>
            {% endif %}

            <!-- CTA -->
            <div style="text-align:center; margin-top:8px;">
                <a href="{{ dashboard_url }}"
                   style="display:inline-block; background:#2563eb; color:#ffffff; text-decoration:none;
                          padding:14px 32px; border-radius:10px; font-size:0.92rem; font-weight:700;">
                    Acessar Dashboard →
                </a>
            </div>

        </div>

        <!-- Footer -->
        <div style="background:#f9fafb; border-top:1px solid #e5e7eb; padding:20px 32px; text-align:center;">
            <p style="font-size:0.78rem; color:#9ca3af; margin:0;">
                Você está recebendo este email porque tem uma conta no <strong>TaskFlow</strong>.<br>
                Este é um email automático enviado diariamente às 8h.
            </p>
        </div>

    </div>
</body>
</html>
"""


def send_daily_digest(app):
    with app.app_context():
        today    = date.today()
        from datetime import timedelta
        tomorrow = today + timedelta(days=1)

        users = User.query.all()

        for user in users:
            if not user.email_notifications:
                continue

            tasks = Task.query.filter_by(user_id=user.id).all()

            today_tasks    = [t for t in tasks if t.due_date == today    and t.status != "concluída"]
            tomorrow_tasks = [t for t in tasks if t.due_date == tomorrow and t.status != "concluída"]
            overdue_tasks  = [t for t in tasks if t.due_date and t.due_date < today and t.status != "concluída"]

            if not today_tasks and not tomorrow_tasks and not overdue_tasks:
                continue

            html_body = render_template_string(
                EMAIL_TEMPLATE,
                name=user.name.split()[0],
                today_tasks=today_tasks,
                tomorrow_tasks=tomorrow_tasks,
                overdue_tasks=overdue_tasks,
                dashboard_url="https://taskflow-webapp-production.up.railway.app/dashboard"
            )

            msg = Message(
                subject="📋 TaskFlow — Resumo diário das suas tarefas",
                recipients=[user.email],
                html=html_body
            )

            try:
                mail.send(msg)
            except Exception as e:
                print(f"Erro ao enviar email para {user.email}: {e}")