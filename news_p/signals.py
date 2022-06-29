from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post

from NewsPortal.settings import DEFAULT_FROM_EMAIL


@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, *args, **kwargs):
    redirectURL = f"/post/{instance.get_absolute_categoryType()}/{str(instance.id)}"

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
