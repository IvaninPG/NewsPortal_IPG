from django.contrib import admin
from .models import Category, Author, Post, Comment

@admin.register(Author, Category, Comment)
class AuthorAdmin(admin.ModelAdmin):
    pass

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass
# admin.site.register(Author)
# admin.site.register(Category)
# admin.site.register(Post)
# admin.site.register(Comment)

