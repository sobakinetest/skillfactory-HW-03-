from django import forms
from .models import Post
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.username = user.email
        user.save()
        try:
            common_group = Group.objects.get(name='common')
            common_group.user_set.add(user)
        except Group.DoesNotExist:
            pass
        return user

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'categories']

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)  # Получаем автора из kwargs
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if self.author:
            # Проверяем количество новостей за последние 24 часа
            from django.utils import timezone
            cutoff = timezone.now() - timezone.timedelta(days=1)
            recent_posts = Post.objects.filter(
                author=self.author,
                created_at__gte=cutoff
            ).count()

            if recent_posts >= 3:
                raise forms.ValidationError(
                    'Вы не можете публиковать более 3 постов в сутки.'
                )

        return cleaned_data