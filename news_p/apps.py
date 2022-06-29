from django.apps import AppConfig


class NewsPConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news_p'

    def ready(self):
        import news_p.signals
