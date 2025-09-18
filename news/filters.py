import django_filters
from .models import Post, Author
from django import forms


class NewsFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Заголовок содержит'
    )

    author = django_filters.ModelChoiceFilter(
        field_name='author',
        queryset=Author.objects.all(),
        label='Автор',
        empty_label='Все авторы'
    )

    created_at = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Дата публикации (после)',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Post
        fields = []