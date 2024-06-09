from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_signal_simplejwt.settings')

# Create a Celery instance
app = Celery('drf_signal_simplejwt')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks from all registered apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# if __name__ == '__main__':
#     app.start()
#     # Start the Celery worker
#     app.worker_main(['--loglevel=info'])
