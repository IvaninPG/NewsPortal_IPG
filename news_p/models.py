from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.urls import reverse


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)                        # поле Автор со связью 1 to 1 с встроенной моделью User (испортированно)
    ratingAuthor = models.SmallIntegerField(default=0)                                       # поле Рейтинг Автора, по умолчанию 0

    def update_rating(self):                                                                 # метод обновления сумарного рейтинга за все
        postRat = self.post_set.aggregate(postRating=Sum('rating'))                          # собирает (aggregate) все рейтинге в моделе пост связанные с конкретным автором и сумирует их
        pRat = 0
        pRat += postRat.get('postRating')

        commentRat = self.authorUser.comment_set.aggregate(commentRating=Sum('rating'))      # собирает (aggregate) все рейтинге в моделе пост связанные с конкретным автором и сумирует их
        cRat = 0
        cRat += commentRat.get('commentRating')

        self.ratingAuthor = pRat * 3 + cRat                                                  # с кладывается обе суммы при этом рейтинг поста умножается на 3
        self.save()

    def __str__(self):
        return self.authorUser.username


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)    # поле Имени с лимитом символов 2 в степени 6 (принято брать 2 в степени n) и оно уникальное.
    subscribers = models.ManyToManyField(User)

    def __str__(self):
        return self.name

class Post(models.Model):
    news = 'NW'
    articls = 'AT'
    CATEGORY = [
        (news, 'Новость'),
        (articls, 'Статья')
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)                     # поле автор со связью 1 to many c моделью Автор
    categoryType = models.CharField(max_length=2, choices=CATEGORY)                  # поле типа информации, лимит 2 символа, с выбором из CATEGOTY, по умолчанию Articl
    dateCreation = models.DateTimeField(auto_now_add=True)                           # поле даты создание с функцией автоматического добавления
    postCategory = models.ManyToManyField(Category, through='PostCategory')          # поле со связью Many to Many c моделью Category и промежуточной моделью PostCategory
    title = models.CharField(max_length=128)                                         # поле заголовок с ограничением 128 символов
    text = models.TextField()                                                        # поле основной статьи
    rating = models.SmallIntegerField(default=0)


    def like(self):  # методЛайка
        self.rating += 1    # Добавляем 1
        self.save()         # сохраняем результат изменения

    def dislike(self):  # метод Дизлайка
        self.rating -= 1    # отнимаем 1
        self.save()         # сохраняем результат изменения

    def preview(self):
        return '{} ... {}'.format(self.text[0:123], str(self.rating))

    def __str__(self):
        return '{}. Rating: {}'.format(self.title, str(self.rating))

    def get_absolute_url(self):
        if self.categoryType =='NW':
            return reverse('post_detail', args=[str(self.id)])
        else:
            return reverse('post_detail', args=[str(self.id)])

        # ИСПРАВИТЬ возвращает имя константы для использования в URL
    def get_absolute_categoryType(self):
        if self.categoryType == 'NW':
            return 'news'
        else:
            return 'articls'



class PostCategory(models.Model):                                                # промежуточная модель для связи Many to maty
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)              # поле связи 1 to Many с моделью Post
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)      # поле связи 1 to Many с моделью Catego


class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)  # поле связи 1 to Many с моделью Post
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)  # поле связи 1 to Many с моделью User, если хотим чтоб коментировал любой пользователь
    text = models.TextField()                                        # поле основной статьи
    dateCreation = models.DateTimeField(auto_now_add=True)           # поле даты созданиz с функцией автоматического добавления
    rating = models.SmallIntegerField(default=0)

    def like(self):  # методЛайка
        self.rating += 1    # Добавляем 1
        self.save()         # сохраняем результат изменения

    def dislike(self):  # метод Дизлайка
        self.rating -= 1    # отнимаем 1
        self.save()         # сохраняем результат изменения
