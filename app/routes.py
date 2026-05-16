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

@main.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logout realizado com sucesso!", "success")

    return redirect(url_for("main.login"))