import os
from celery import Celery
from celery.schedules import crontab

    # Celery - отправка по метке во views.py в отдельном терминале: celery -A NewsPortal worker -l INFO -P gevent
    # установить pip install gevent чтоб работает, иначе received без действия.
    # [2022-06-28 11:11:32,648: INFO/MainProcess] Task news_p.tasks.printer[e0bfb01e-1db0-44ea-9577-0f971ae70522] received
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPortal.settings')

app = Celery('NewsPortal')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

    # Celery - отправка по расписанию в отдельном терминале: celery -A NewsPortal beat -l INFO
app.conf.beat_schedule = {
    'weekly_newsletter_monday_8am': {
        'task': 'news_p.tasks.weekly_newsletter',
        'schedule':  crontab(hour=8, minute=0, day_of_week='monday'),
        'args': (),
    },
}
