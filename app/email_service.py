import os
from datetime import date, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import render_template_string
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

        <div style="background:#2563eb; padding:28px 32px; text-align:center;">
            <span style="color:#ffffff; font-size:1.3rem; font-weight:800;">✓ TaskFlow</span>
            <p style="color:rgba(255,255,255,0.85); margin:10px 0 0; font-size:0.92rem;">Resumo diário de tarefas</p>
        </div>

        <div style="padding:32px;">

            <p style="font-size:1rem; color:#111827; margin:0 0 24px;">
                Olá, <strong>{{ name }}</strong>! 👋 Aqui está o resumo das suas tarefas para hoje.
            </p>

            {% if today_tasks %}
            <div style="margin-bottom:24px;">
                <h2 style="font-size:0.95rem; font-weight:800; color:#111827; margin:0 0 12px;">📅 VENCEM HOJE</h2>
                {% for task in today_tasks %}
                <div style="background:#fffbeb; border:1.5px solid #fde68a; border-radius:10px; padding:14px 16px; margin-bottom:8px;">
                    <div style="font-size:0.92rem; font-weight:700; color:#111827; margin-bottom:4px;">{{ task.title }}</div>
                    {% if task.description %}
                    <div style="font-size:0.82rem; color:#6b7280;">{{ task.description[:80] }}{% if task.description|length > 80 %}...{% endif %}</div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% if tomorrow_tasks %}
            <div style="margin-bottom:24px;">
                <h2 style="font-size:0.95rem; font-weight:800; color:#111827; margin:0 0 12px;">➡️ VENCEM AMANHÃ</h2>
                {% for task in tomorrow_tasks %}
                <div style="background:#eff6ff; border:1.5px solid #bfdbfe; border-radius:10px; padding:14px 16px; margin-bottom:8px;">
                    <div style="font-size:0.92rem; font-weight:700; color:#111827; margin-bottom:4px;">{{ task.title }}</div>
                    {% if task.description %}
                    <div style="font-size:0.82rem; color:#6b7280;">{{ task.description[:80] }}{% if task.description|length > 80 %}...{% endif %}</div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% if overdue_tasks %}
            <div style="margin-bottom:24px;">
                <h2 style="font-size:0.95rem; font-weight:800; color:#dc2626; margin:0 0 12px;">⚠️ ATRASADAS</h2>
                {% for task in overdue_tasks %}
                <div style="background:#fff1f2; border:1.5px solid #fca5a5; border-radius:10px; padding:14px 16px; margin-bottom:8px;">
                    <div style="font-size:0.92rem; font-weight:700; color:#111827; margin-bottom:4px;">{{ task.title }}</div>
                    <div style="font-size:0.78rem; color:#dc2626; font-weight:600;">Venceu em {{ task.due_date.strftime("%d/%m/%Y") }}</div>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% if not today_tasks and not tomorrow_tasks and not overdue_tasks %}
            <div style="text-align:center; padding:32px; background:#f0fdf4; border-radius:12px; margin-bottom:24px;">
                <div style="font-size:2rem; margin-bottom:8px;">🎉</div>
                <p style="font-size:0.92rem; font-weight:700; color:#16a34a; margin:0;">Tudo em dia!</p>
            </div>
            {% endif %}

            <div style="text-align:center; margin-top:24px;">
                <a href="https://taskflow-webapp-production.up.railway.app/dashboard"
                   style="display:inline-block; background:#2563eb; color:#ffffff; text-decoration:none;
                          padding:14px 32px; border-radius:10px; font-size:0.92rem; font-weight:700;">
                    Acessar Dashboard →
                </a>
            </div>

        </div>

        <div style="background:#f9fafb; border-top:1px solid #e5e7eb; padding:20px 32px; text-align:center;">
            <p style="font-size:0.78rem; color:#9ca3af; margin:0;">
                Email automático do <strong>TaskFlow</strong> — enviado quando você tem tarefas vencendo.
            </p>
        </div>

    </div>
</body>
</html>
"""


def send_daily_digest(app):
    with app.app_context():
        today    = date.today()
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
                overdue_tasks=overdue_tasks
            )

            message = Mail(
                from_email="taskflow.notificacoes@gmail.com",
                to_emails=user.email,
                subject="📋 TaskFlow — Resumo diário das suas tarefas",
                html_content=html_body
            )

            try:
                sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
                sg.send(message)
            except Exception as e:
                print(f"Erro ao enviar email para {user.email}: {e}")