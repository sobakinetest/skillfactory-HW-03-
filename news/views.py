from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.http import Http404
from django.core.paginator import Paginator
from .models import Author, Post, Category, PostCategory
from .filters import NewsFilter
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages


# ==================== БАЗОВЫЕ КЛАССЫ ====================

class BasePostCreate(CreateView):
    """Базовый класс для создания постов"""
    permission_required = 'news.add_post'
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    post_type = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        author, created = Author.objects.get_or_create(user=self.request.user)
        kwargs['author'] = author
        return kwargs

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = self.post_type

        author, created = Author.objects.get_or_create(user=self.request.user)
        post.author = author

        post.save()
        categories = form.cleaned_data.get('categories')
        post.categories.add(*categories)
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class BasePostDetail(DetailView):
    model = Post
    context_object_name = 'newsdetail'
    post_type = None  # Определяется в дочерних классах
    template_name = None  # Определяется в дочерних классах

    def get_queryset(self):
        return Post.objects.filter(post_type=self.post_type)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class BasePostEdit(LoginRequiredMixin, UpdateView):
    """Базовый класс для редактирования постов"""
    permission_required = 'news.change_post'
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    login_url = '/accounts/login/'
    post_type = None  # Определяется в дочерних классах
    context_post_type = None  # Для контекста

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.post_type != self.post_type:
            raise Http404("Пост не найден")
        if obj.author.user != self.request.user:
            raise Http404("Вы не автор этого поста")
        return obj

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = self.context_post_type
        return context


class BasePostDelete(DeleteView):
    """Базовый класс для удаления постов"""
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news:news_list')
    post_type = None  # Определяется в дочерних классах

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.post_type != self.post_type:
            raise Http404("Пост не найден")
        return obj


# ==================== КЛАССЫ СОЗДАНИЯ ====================

class NewsCreate(BasePostCreate):
    post_type = 'NW'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = 'Новость'
        return context


class ArticleCreate(BasePostCreate):
    post_type = 'AR'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = 'Статью'
        return context


# ==================== КЛАССЫ ПРОСМОТРА ====================

class NewsDetail(BasePostDetail):
    post_type = 'NW'
    template_name = 'news_detail.html'


class ArticleDetail(BasePostDetail):
    post_type = 'AR'
    template_name = 'article_detail.html'


# ==================== КЛАССЫ РЕДАКТИРОВАНИЯ ====================

class NewsEdit(BasePostEdit):
    post_type = 'NW'
    context_post_type = 'Новость'


class ArticleEdit(BasePostEdit):
    post_type = 'AR'
    context_post_type = 'Статью'


# ==================== КЛАССЫ УДАЛЕНИЯ ====================

class NewsDelete(BasePostDelete):
    post_type = 'NW'


class ArticleDelete(BasePostDelete):
    post_type = 'AR'


# ==================== ОСТАЛЬНЫЕ КЛАССЫ И ФУНКЦИИ ====================

class NewsList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news_list.html'
    context_object_name = 'newslist'
    paginate_by = 10


def news_search(request):
    filter = NewsFilter(request.GET, queryset=Post.objects.all())
    paginator = Paginator(filter.qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news_search.html', {
        'filter': filter,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    })


class CategoryListView(ListView):
    model = Category
    template_name = 'categories.html'
    context_object_name = 'categories'
    paginate_by = 6


@login_required
def make_me_author(request):
    Author.objects.get_or_create(user=request.user)
    authors_group, created = Group.objects.get_or_create(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(request.user)
    return redirect('news:news_list')

@login_required
@require_POST
def subscribe(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.subscribers.add(request.user)
    messages.success(request, f'Вы подписались на категорию «{category.name}»')
    return redirect('news:category_list')


@login_required
@require_POST
def unsubscribe(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.subscribers.remove(request.user)
    messages.success(request, f'Вы отписались от категории «{category.name}»')
    return redirect('news:category_list')