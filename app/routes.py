# Rotas da aplicação
from flask import Blueprint, render_template, request, redirect, url_for, flash

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from .models import User, Task
from .extensions import db, bcrypt
from datetime import datetime, date

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        user_exists = User.query.filter_by(email=email).first()

        if user_exists:
            flash("Este e-mail já está cadastrado.", "error")
            return redirect(url_for("main.register"))

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Conta criada com sucesso! Faça login.", "success")

        return redirect(url_for("main.login"))

    return render_template("register.html")


@main.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            flash("Login realizado com sucesso!", "success")

            return redirect(url_for("main.dashboard"))

        flash("E-mail ou senha incorretos.", "error")

        return redirect(url_for("main.login"))

    return render_template("login.html")


@main.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    if request.method == "POST":

        title = request.form.get("title")

        description = request.form.get("description")

        priority = request.form.get("priority")

        due_date = request.form.get("due_date")

        due_date_obj = None

        if due_date:

            due_date_obj = datetime.strptime(
                due_date,
                "%Y-%m-%d"
            ).date()

        new_task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date_obj,
            user_id=current_user.id
        )

        db.session.add(new_task)

        db.session.commit()

        flash(
            "Tarefa criada com sucesso!",
            "success"
        )

        return redirect(
            url_for("main.dashboard")
        )

    tasks_query = Task.query.filter_by(
        user_id=current_user.id
    )

    tasks = tasks_query.all()

    priority_order = {
        "alta": 1,
        "media": 2,
        "baixa": 3
    }

    tasks = sorted(
        tasks,
        key=lambda task: (

            task.status == "concluída",

            priority_order.get(
                task.priority,
                4
            ),

            task.due_date is None,

            task.due_date
        )
    )

    today = date.today()

    total_tasks = len(tasks)

    completed_tasks = len([
        task for task in tasks
        if task.status == "concluída"
    ])

    pending_tasks = len([
        task for task in tasks
        if task.status == "pendente"
    ])

    overdue_tasks = len([

        task for task in tasks

        if (
            task.due_date
            and task.due_date < today
            and task.status != "concluída"
        )

    ])

    return render_template(
        "dashboard.html",

        tasks=tasks,

        today=today,

        total_tasks=total_tasks,

        completed_tasks=completed_tasks,

        pending_tasks=pending_tasks,

        overdue_tasks=overdue_tasks
    )

@main.route("/task/<int:task_id>/complete")
@login_required
def complete_task(task_id):

    task = Task.query.get_or_404(task_id)

    if task.owner != current_user:
        flash("Acesso não autorizado.", "error")
        return redirect(url_for("main.dashboard"))

    task.status = "concluída"

    db.session.commit()

    flash("Tarefa concluída!", "success")

    return redirect(url_for("main.dashboard"))


@main.route("/task/<int:task_id>/delete")
@login_required
def delete_task(task_id):

    task = Task.query.get_or_404(task_id)

    if task.owner != current_user:
        flash("Acesso não autorizado.", "error")
        return redirect(url_for("main.dashboard"))

    db.session.delete(task)

    db.session.commit()

    flash("Tarefa excluída!", "success")

    return redirect(url_for("main.dashboard"))


@main.route("/task/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):

    task = Task.query.get_or_404(task_id)

    if task.owner != current_user:
        flash("Acesso não autorizado.", "error")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":

        task.title = request.form.get("title")

        task.description = request.form.get("description")

        task.priority = request.form.get("priority")

        task.status = request.form.get("status")

        due_date_str = request.form.get("due_date")

        if due_date_str:
            task.due_date = datetime.strptime(
                due_date_str,
                "%Y-%m-%d"
            ).date()

        else:
            task.due_date = None

        db.session.commit()

        flash("Tarefa atualizada com sucesso!", "success")

        return redirect(url_for("main.dashboard"))

    return render_template(
        "edit_task.html",
        task=task
    )

@main.route("/task/<int:task_id>/update-status", methods=["POST"])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
 
    if task.owner != current_user:
        return {"error": "Acesso não autorizado."}, 403
 
    data = request.get_json()
    new_status = data.get("status")
 
    valid_statuses = ["pendente", "em_progresso", "concluída"]
 
    if new_status not in valid_statuses:
        return {"error": "Status inválido."}, 400
 
    task.status = new_status
    db.session.commit()
 
    return {"success": True, "status": new_status}, 200

@main.route("/quadro")
@login_required
def quadro():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("quadro.html", tasks=tasks)

# Substitui a rota /perfil existente no routes.py

@main.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_avatar":
            avatar = request.form.get("avatar")
            if avatar in ['🐱', '🐶', '🦊', '🐼', '🐸']:
                current_user.avatar = avatar
                db.session.commit()
                flash("Avatar atualizado com sucesso!", "success")

        elif action == "update_notifications":
            current_user.email_notifications = request.form.get("email_notifications") == "on"
            db.session.commit()
            flash("Preferências de notificação atualizadas!", "success")
            name = request.form.get("name")
            if name:
                current_user.name = name
                db.session.commit()
                flash("Nome atualizado com sucesso!", "success")

        elif action == "update_password":
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")

            if not bcrypt.check_password_hash(current_user.password, current_password):
                flash("Senha atual incorreta.", "error")
            elif new_password != confirm_password:
                flash("As senhas não coincidem.", "error")
            elif len(new_password) < 6:
                flash("A nova senha deve ter pelo menos 6 caracteres.", "error")
            else:
                current_user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
                db.session.commit()
                flash("Senha atualizada com sucesso!", "success")

        return redirect(url_for("main.perfil"))

    return render_template("perfil.html")

@main.route("/analytics")
@login_required
def analytics():
    from datetime import date, timedelta

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    today = date.today()

    total_tasks     = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == "concluída"])
    pending_tasks   = len([t for t in tasks if t.status == "pendente"])
    progress_tasks  = len([t for t in tasks if t.status == "em_progresso"])
    overdue_tasks   = len([t for t in tasks if t.due_date and t.due_date < today and t.status != "concluída"])
    high_tasks      = len([t for t in tasks if t.priority == "alta"])
    medium_tasks    = len([t for t in tasks if t.priority == "media"])
    low_tasks       = len([t for t in tasks if t.priority == "baixa"])
    completion_rate = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
    created_this_week = len([t for t in tasks if t.created_at.date() >= today - timedelta(days=7)])

    week_labels = []
    week_data   = []
    days_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        week_labels.append(days_pt[day.weekday()])
        week_data.append(len([t for t in tasks if t.created_at.date() == day]))

    return render_template("analytics.html",
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        progress_tasks=progress_tasks,
        overdue_tasks=overdue_tasks,
        high_tasks=high_tasks,
        medium_tasks=medium_tasks,
        low_tasks=low_tasks,
        completion_rate=completion_rate,
        created_this_week=created_this_week,
        week_labels=week_labels,
        week_data=week_data
    )

@main.route("/perfil/update", methods=["POST"])
@login_required
def perfil_update():
    from flask import jsonify
    data   = request.get_json()
    action = data.get("action")

    if action == "update_avatar":
        avatar = data.get("avatar")
        if avatar not in ['🐱', '🐶', '🦊', '🐼', '🐸']:
            return jsonify({"error": "Avatar inválido."}), 400
        current_user.avatar = avatar
        db.session.commit()
        return jsonify({"success": True})

    elif action == "update_name":
        name = data.get("name", "").strip()
        if not name:
            return jsonify({"error": "Nome não pode ser vazio."}), 400
        current_user.name = name
        db.session.commit()
        return jsonify({"success": True})

    elif action == "update_notifications":
        current_user.email_notifications = data.get("email_notifications", True)
        db.session.commit()
        return jsonify({"success": True})

    return jsonify({"error": "Ação inválida."}), 400

@main.route("/test-email")
@login_required
def test_email():
    try:
        import os
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        message = Mail(
            from_email="taskflow.notificacoes@gmail.com",
            to_emails=current_user.email,
            subject="Teste TaskFlow",
            html_content="<h1>Teste de email do TaskFlow!</h1><p>Se você recebeu este email, as notificações estão funcionando.</p>"
        )

        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        sg.send(message)
        flash("Email enviado!", "success")
    except Exception as e:
        flash(f"Erro: {str(e)}", "error")
    return redirect(url_for("main.dashboard"))

@main.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logout realizado com sucesso!", "success")

    return redirect(url_for("main.login"))