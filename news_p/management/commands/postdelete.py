from django.core.management.base import BaseCommand, CommandError
from ...models import Post, Category

class Command(BaseCommand):
    help = 'Удаляет все новости выбранной категории'

    def add_arguments(self, parser):
        parser.add_argument(
            'Category',
            type=str)


    def handle(self, *args, **options):
        self.stdout.write(f"Вы действительно хотите удалить все посты категории {options['Category']}? yes/no")
        answer = input()

        if answer !='yes':
            self.stdout.write(self.style.ERROR('Отмена команды'))

        else:
            try:
                category = Category.objects.get(name=options['Category'])
                Post.objects.filter(postCategory=category).delete()
                self.stdout.write(self.style.SUCCESS('Посты успешно удалены!'))

            except Category.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Категория {options["Category"]} не найдена'))

