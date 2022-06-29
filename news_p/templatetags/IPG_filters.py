from django import template

# Импортируем модуль для работы с регулярными выражениями
import re


register = template.Library()



@register.filter()
def censor(value):
   """
   value: значение, к которому нужно применить фильтр
   """
   # список ценцурируемых слова
   swear_word = ["сука", "пидорас", "мудак", "хуй"]

   # цикл проверяющий поочереди наличие в value слов из swear_word
   for word in swear_word:

      # при помощи метода "re.sub" модуля "re" проверяем "Value" на наличие
      # в нем "word" начинающегося со строчной или заглавной буквы, и при обнаружении
      # меняющий в нем все буквы на точки кроме первой и последней
      value = re.sub(f'{word}|{word[0].upper() + word[1:]}', f'{word[0]}{"." * (len(word) - 1)}{word[-1]}', value)

   return f'{value}'