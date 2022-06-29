import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
import datetime
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
# from NewsPortal.news_p.models import Post
from django.core.mail import EmailMultiAlternatives

from NewsPortal.settings import DEFAULT_FROM_EMAIL
from django.template.loader import render_to_string

from ...models import Post

logger = logging.getLogger(__name__)


def my_job():
    # Your job processing logic here...

    weekEarlier = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(days=7)

    for u in User.objects.all():

        categoryList = list(u.category_set.all().values_list('name', flat=True))

        if len(categoryList):
            qs = Post.objects.filter(dateCreation__gt=weekEarlier).filter(postCategory__in=u.category_set.all())
            subject = f'Ваши еженедельные новости: {", ".join(categoryList)} за период c {weekEarlier.strftime("%d.%m.%Y")}'
            body = f'News are: {". ".join(list(qs.values_list("title", flat=True)))}'
            # print(f'Это u = {u}')
            # print('-------')
            # print(f'Это qs = {qs}')
            # print('-------')
            # print(f'Это subject = {subject}')
            # print('-------')
            # print(f'Это body = {body}')
            # print('-------')
            html_content = render_to_string(
                'weekly_mail.html',
                {
                    'posts_list': qs,
                    'user': u,
                    'subject': subject
                    # 'redirectURL' = redirectURL
                }
            )
            # mailing list
            mailing_list = [u.email]
            if len(mailing_list):
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=body,
                    from_email=DEFAULT_FROM_EMAIL,
                    to=mailing_list
                )
                msg.attach_alternative(html_content, 'text/html')
                msg.send()
                # print(mailing_list)
                # print('-------')
                # print(f'Это mailing_list = {mailing_list}')
                # print('---Все----')




# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="sun"),  # Every 1 weec
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")