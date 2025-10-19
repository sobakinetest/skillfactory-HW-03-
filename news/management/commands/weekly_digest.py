from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from news.models import Category, Post


class Command(BaseCommand):
    help = 'Еженедельная рассылка новых статей'

    def handle(self, *args, **options):
        self.stdout.write("Запуск еженедельной рассылки...")

        week_ago = timezone.now() - timedelta(days=7)
        emails_sent = 0

        for category in Category.objects.all():
            subscribers = category.subscribers.all()
            if not subscribers.exists():
                continue

            new_posts = category.posts.filter(created_at__gte=week_ago).order_by('-created_at')

            if not new_posts.exists():
                continue

            self.stdout.write(f"{category.name}: {new_posts.count()} постов, {subscribers.count()} подписчиков")

            for subscriber in subscribers:
                try:
                    posts_with_urls = []
                    for post in new_posts:
                        posts_with_urls.append({
                            'title': post.title,
                            'author': post.author.user.username,
                            'created_at': post.created_at,
                            'preview': post.preview(),
                            'url': f"http://127.0.0.1:8000{post.get_absolute_url()}"
                        })

                    html_content = render_to_string(
                        'email/weekly_digest.html',
                        {
                            'subscriber': subscriber,
                            'category': category,
                            'new_posts': posts_with_urls,
                            'week_ago': week_ago,
                        }
                    )
                    text_content = strip_tags(html_content)

                    subject = f'Еженедельная рассылка: новые статьи в категории "{category.name}"'

                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[subscriber.email]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send(fail_silently=False)
                    emails_sent += 1

                except Exception as e:
                    self.stderr.write(f"Ошибка для {subscriber.email}: {e}")

        self.stdout.write(
            self.style.SUCCESS(f'Рассылка завершена! Отправлено писем: {emails_sent}')
        )