from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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
from .models import Author, Post
from .filters import NewsFilter
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

class NewsList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news_list.html'
    context_object_name = 'newslist'
    paginate_by = 10


class NewsDetail(DetailView):
    model = Post
    template_name = 'news_detail.html'
    context_object_name = 'newsdetail'

    def get_queryset(self):
        return Post.objects.filter(post_type='NW')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class ArticleDetail(DetailView):
    model = Post
    template_name = 'article_detail.html'
    context_object_name = 'newsdetail'

    def get_queryset(self):
        return Post.objects.filter(post_type='AR')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context

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


class NewsCreate(CreateView):
    permission_required = 'news.add_post'
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'NW'
        post.author, created = Author.objects.get_or_create(user=self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('news:news_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = 'Новость'
        return context


class NewsEdit(LoginRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    login_url = '/accounts/login/'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.post_type != 'NW':
            raise Http404("Пост не найден")

        if obj.author.user != self.request.user:
            raise Http404("Вы не автор этого поста")
        return obj

    def get_success_url(self):
        return reverse_lazy('news:news_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = 'Новость'
        return context

class NewsDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news:news_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.post_type != 'NW':
            raise Http404("Пост не найден")
        return obj

class ArticleCreate(CreateView):
    permission_required = 'news.add_post'
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.post_type = 'AR'
        post.author, created = Author.objects.get_or_create(user=self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('news:news_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = 'Статью'
        return context


class ArticleEdit(LoginRequiredMixin, UpdateView):
    permission_required = 'news.change_post'
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    login_url = '/accounts/login/'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.post_type != 'AR':
            raise Http404("Пост не найден")
        if obj.author.user != self.request.user:
            raise Http404("Вы не автор этого поста")
        return obj

    def get_success_url(self):
        return reverse_lazy('news:news_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = 'Статью'
        return context

class ArticleDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news:news_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.post_type != 'AR':
            raise Http404("Пост не найден")
        return obj


@login_required
def make_me_author(request):
    Author.objects.get_or_create(user=request.user)
    authors_group, created = Group.objects.get_or_create(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(request.user)

    return redirect('news:news_list')
