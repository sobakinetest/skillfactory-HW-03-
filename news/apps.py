from django.apps import AppConfig
import threading
import time
from datetime import datetime
import os


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        import news.signals
        print("Сигналы зарегистрированы")

        if os.environ.get('RUN_MAIN') or not os.environ.get('DJANGO_AUTO_RELOAD'):
            self.start_scheduler()

    def start_scheduler(self):

        def scheduler_loop():
            print("Планировщик запущен (проверка каждый понедельник 9:00)")
            last_run = None

            while True:
                try:
                    now = datetime.now()

                    is_monday_9am = (now.weekday() == 0 and
                                     now.hour == 9 and
                                     now.minute == 0)

                    if is_monday_9am and last_run != now.date():
                        print("Время для еженедельной рассылки!")

                        from django.core.management import call_command
                        call_command('weekly_digest')

                        last_run = now.date()
                        print("Рассылка завершена")

                        time.sleep(120)

                    time.sleep(60)

                except Exception as e:
                    print(f"Ошибка в планировщике: {e}")
                    time.sleep(300)


        thread = threading.Thread(target=scheduler_loop, daemon=True)
        thread.start()
        print("Планировщик запущен успешно!")