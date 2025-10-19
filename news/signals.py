from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Post
import os


@receiver(post_save, sender=Post)
def notify_subscribers_on_post_create(sender, instance, created, **kwargs):
    if not created or kwargs.get('raw', False) or os.environ.get('DJANGO_AUTO_RELOAD'):
        return

    print(f"Новая публикация: '{instance.title}'")

    import threading
    def delayed_notification():
        import time
        time.sleep(1)
        send_post_notifications(instance)

    thread = threading.Thread(target=delayed_notification, daemon=True)
    thread.start()


def send_post_notifications(instance):
    instance.refresh_from_db()
    categories = instance.categories.all()

    print(f"Найдено категорий: {categories.count()}")

    if not categories.exists():
        print("У поста нет категорий")
        return

    absolute_url = f"http://127.0.0.1:8000{instance.get_absolute_url()}"

    for category in categories:
        subscribers = category.subscribers.all()
        print(f"Категория '{category.name}': {subscribers.count()} подписчиков")

        if not subscribers.exists():
            continue

        preview = instance.content[:50] + '...' if len(instance.content) > 50 else instance.content
        subject = f'Новость в категории «{category.name}»: {instance.title}'

        html_content = render_to_string(
            'email/new_post_notification.html',
            {
                'category': category,
                'post': instance,
                'preview': preview,
                'post_url': absolute_url,
            }
        )

        text_content = f"""
Здравствуйте!

В вашей любимой категории «{category.name}» появилась новая статья:
{instance.title}

Краткое содержание:
{preview}

Читать полностью: {absolute_url}

Это автоматическое письмо. Пожалуйста, не отвечайте на него.
"""

        for subscriber in subscribers:
            try:
                text_content_with_name = text_content.replace('{{subscriber.username}}', subscriber.username)

                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content_with_name,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[subscriber.email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=True)
                print(f"Письмо отправлено: {subscriber.email}")
            except Exception as e:
                print(f"Ошибка отправки {subscriber.email}: {e}")