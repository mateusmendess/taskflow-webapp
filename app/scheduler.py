from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz


def init_scheduler(app):
    from .email_service import send_daily_digest

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        func=send_daily_digest,
        trigger=CronTrigger(hour=8, minute=0, timezone=pytz.timezone("America/Sao_Paulo")),
        args=[app],
        id="daily_digest",
        name="Envio diário de resumo de tarefas",
        replace_existing=True
    )

    scheduler.start()
    return scheduler