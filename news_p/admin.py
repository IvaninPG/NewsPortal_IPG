from django.contrib import admin
from .models import Category, Author, Post, Comment, PostCategory


class PostCategoryline(admin.TabularInline):
    model = PostCategory
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # в панеле редактировании добавляется поле где можно добавить или поменять категорию из PostCategory
    inlines = [
        PostCategoryline,
    ]
    # exclude = ('postCategory',)
    list_display = ('title', 'categoryType', 'author', 'postCategory_list', 'text', 'dateCreation')
    list_filter = ('categoryType', 'author', 'dateCreation')
    list_per_page = 10
    save_as = True
    save_on_top = True
    search_fields = ('title', 'categoryType')
    search_help_text = 'Введите искомое слово без учета регистра'
    view_on_site = False

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('authorUser', 'ratingAuthor')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Comment._meta.get_fields()]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'subscribers_list',)
