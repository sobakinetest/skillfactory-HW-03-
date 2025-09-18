from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from news.resources import POST_TYPES
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        from .models import Comment

        post_rating = self.post_set.aggregate(pr=Sum('rating'))['pr'] or 0
        post_rating *= 3

        comment_rating = self.user.comment_set.aggregate(cr=Sum('rating'))['cr'] or 0

        post_comment_rating = Comment.objects.filter(post__author=self).aggregate(pcr=Sum('rating'))['pcr'] or 0

        self.rating = post_rating + comment_rating + post_comment_rating
        self.save()

    def __str__(self):
        return f'{self.user.username} (rating: {self.rating})'


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POST_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    rating = models.IntegerField(default=0)
    categories = models.ManyToManyField(Category, through='PostCategory')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.content[:124] + '...' if len(self.content) > 124 else self.content

    def __str__(self):
        return f'{self.title} ({self.get_post_type_display()}, автор: {self.author.user.username})'

    def get_absolute_url(self):
        if self.post_type == 'NW':
            return reverse('news:news_detail', kwargs={'pk': self.pk})
        else:
            return reverse('articles:article_detail', kwargs={'pk': self.pk})

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = [['post', 'category']]


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)  # Используем строковую ссылку
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f'Комментарий от {self.user.username} к посту "{self.post.title}"'

    class Meta:
        ordering = ['-created_at']
