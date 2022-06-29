from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Post


class PostForm(forms.ModelForm):
   text = forms.TextInput()

   class Meta:
       model = Post
       fields = [
           'author',
           'postCategory',
           'title',
           'text',
       ]
       # model = Subscribers
       # # fields = '__all__'
       # fields = [
       #     'category'
       # ]


   def clean(self):
       cleaned_data = super().clean()
       text = cleaned_data.get("text")
       title = cleaned_data.get("title")

       if title == text:
           raise ValidationError(
               "Текст не должен быть идентичен заголовку."
           )

       return cleaned_data\

