from django.urls import path
from .views import (
    ArticleCreate,
    ArticleEdit,
    ArticleDelete,
    NewsList,
    ArticleDetail,
)

app_name = 'articles'

urlpatterns = [
    path('', NewsList.as_view(), name='news_list'),
    path('create/', ArticleCreate.as_view(), name='article_create'),
    path('<int:pk>/', ArticleDetail.as_view(), name='article_detail'),
    path('<int:pk>/edit/', ArticleEdit.as_view(), name='article_edit'),
    path('<int:pk>/delete/', ArticleDelete.as_view(), name='article_delete'),
]