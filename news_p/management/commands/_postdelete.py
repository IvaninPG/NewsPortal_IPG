from django.core.management.base import BaseCommand, CommandError
from ...models import Post

class Command(BaseCommand):
    help = 'Удаляет все новости выбранной категории'

    def add_arguments(self, parser):
        parser.add_argument(
            'Category',
            nargs='+',
            type=str)


    def handle(self, *args, **options):
        self.stdout.readable()
        self.stdout.write(f"Вы действительно хотите удалить все посты категории {options['Category']}? yes/no")
        answer = input()
        if answer =='yes':
            Post.objects.filter(postCategory=options['Category']).delete()
            self.stdout.write(self.style.SUCCESS('Посты успешно удалены!'))
            return

        self.stdout.write(self.style.ERROR('В доступе отказано'))