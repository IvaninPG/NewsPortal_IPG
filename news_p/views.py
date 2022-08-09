
from django.http import HttpRequest
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin

from .filters import PostsSearchFilter
from .forms import PostForm
from .models import Post, Category

from .tasks import notify_subscribers
from django.core.cache import cache

import logging

logger = logging.getLogger(__name__)

class PostsList(ListView):
    template_name = 'posts.html'
        # Это имя списка, в котором будут лежать все объекты
        # для обращения к нему в html-шаблоне.
    context_object_name = 'posts'
        # Указываем количество записей на странице
    paginate_by = 10

    def get_queryset(self):
            # сохраняем функционал родительского get_queryset
            # super().get_queryset()
            # берем из NewsProject/urls.py <categoryType>
        self.categoryType = eval('Post.' + str(self.kwargs['categoryType']))
            # возвращаем объекты отфильтрованне по categoryType
        return Post.objects.filter(categoryType=self.categoryType).order_by('-dateCreation')


class PostsSearchList(PostsList):
    template_name = 'posts_search.html'

    def get_queryset(self):
            # Получаем обычный запрос
        queryset = super().get_queryset()
            # Используем наш класс фильтрации.
            # self.request.GET содержит объект QueryDict
            # Сохраняем нашу фильтрацию в объекте класса,
            # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostsSearchFilter(self.request.GET, queryset)
            # Возвращаем из функции отфильтрованный список постов
        return self.filterset.qs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
            # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def post(self, request, *args, **kwargs):
        category = request.POST['id']
        if Category.objects.get(name=category).subscribers.contains(request.user):
            Category.objects.get(name=category).subscribers.remove(request.user)
        else:
            Category.objects.get(name=category).subscribers.add(request.user)
        return redirect(request.path)

        # Переопределяем метод получения объекта с проверкой есть он в кэш или нет
    def get_object(self, *args, **kwargs):
        obj = cache.get(f'post-{self.kwargs["pk"]}',
                        None)
        print('Это кэш')
        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)
            print('Это из кэш')

        return obj

class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'news_p.add_post'

        # Указываем нашу разработанную форму
    form_class = PostForm
        # модель постов
    model = Post
        # и новый шаблон, в котором используется форма.
    template_name = 'Post_edit.html'

    def form_valid(self, form):
            # Этот метод вызывается, когда действительные данные формы были отправлены.
            # Он должен вернуть HttpResponse.
        post = form.save(commit=False)
            # Склеивает из текста команду post.news или post.articls
        post.categoryType = eval(f"post.{str((self.request.path).split('/')[2])}")
        form.save()
            # команда-метка для Celery с задержкой выполнения 30 сек.
        notify_subscribers.apply_async([post.pk], countdown=30)
             # переопределяем файл success_url с путем куда перенаправить запрос после создания
        self.success_url = f"../{str(post.id)}"


        return super().form_valid(form)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'news_p.change_post'

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = '../'


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'news_p.delete_post'

    model = Post
    template_name = 'post_delete.html'

        # прописываем путь в  success_url взяв из пути news или articls
    def dispatch(self, request, *args, **kwargs):
        self.success_url = f"/post/{self.kwargs['categoryType']}/"
        return super().dispatch(request, *args, **kwargs)
