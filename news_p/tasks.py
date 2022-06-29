from celery import shared_task
from .models import Post
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from NewsPortal.settings import DEFAULT_FROM_EMAIL
import datetime


    # Celery - отправка по метке во views.py в
    # вызывается из views.py class PostCreate
@shared_task
def notify_subscribers(oid):
    instance = Post.objects.get(pk=oid)
    redirectURL = f"/post/{instance.get_absolute_categoryType()}/{str(oid)}"

    html_content = render_to_string(
        'post_created_mail.html',
        {
            'post': instance,
            'redirectURL': redirectURL,
        }
    )

    mailing_list = list(set(instance.postCategory.all().values_list('subscribers__email', flat=True)))

    if mailing_list.count(''):
        mailing_list.remove('')

        print(mailing_list)

    if len(mailing_list):
        msg = EmailMultiAlternatives(
            subject=f'{instance.title}. Автор: {instance.author.authorUser.username}  '
                    f'({instance.dateCreation.strftime("%d.%m.%Y")})',
            body=instance.text,
            from_email=DEFAULT_FROM_EMAIL,
            to=mailing_list
        )
        print(DEFAULT_FROM_EMAIL)
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        print('Сообщение отправлено при помощи Celery')

    # Celery - отправка по расписанию в отдельном терминале: celery -A NewsPortal beat -l INFO
    # вызывается из celery.py
@shared_task
def weekly_newsletter():

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