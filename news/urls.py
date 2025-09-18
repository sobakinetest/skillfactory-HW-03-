from django.urls import path
from .views import (
    NewsList,
    NewsDetail,
    news_search,
    NewsCreate,
    NewsEdit,
    NewsDelete,
    make_me_author,
)

app_name = 'news'

urlpatterns = [
    path('', NewsList.as_view(), name='news_list'),
    path('<int:pk>/', NewsDetail.as_view(), name='news_detail'),
    path('search/', news_search, name='news_search'),
    path('create/', NewsCreate.as_view(), name='news_create'),
    path('<int:pk>/edit/', NewsEdit.as_view(), name='news_edit'),
    path('<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
    path('make_author/', make_me_author, name = 'make_me_author')
]