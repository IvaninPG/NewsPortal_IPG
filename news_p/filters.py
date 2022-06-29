from django.forms import DateInput
from django_filters import FilterSet, DateFilter
from .models import Post
import django_filters

# Создаем свой набор фильтров для модели Product.
# FilterSet, который мы наследуем,
# должен чем-то напомнить знакомые вам Django дженерики.

class PostsSearchFilter(FilterSet):
    date_widget = DateInput()
    date_widget.input_type = 'date'
    dateCreation = DateFilter(
        field_name='dateCreation',
        lookup_expr='gte',
        widget=date_widget,
    )

    class Meta:
            # В Meta классе мы должны указать Django модель,
            # в которой будем фильтровать записи.

            model = Post

            # В fields мы описываем по каким полям модели
            # будет производиться фильтрация.

            fields = {

                # поиск по названию

                'title': ['icontains'],

                # количество товаров должно быть больше или равно

                'postCategory': ['exact']
                # 'dateCreation': ['gt'],  # цена должна быть больше или равна указанной
                }

