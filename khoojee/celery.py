from __future__ import absolute_import
import os
from celery import Celery, shared_task
from invoker.tasks.mobile.controller import controller

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khoojee.settings')
app = Celery('phantom')

app.config_from_object('django.conf.settings', namespace='CELERY')
app.autodiscover_tasks()


@shared_task(name="phantom_ig")
def find_number_details(mobile_number, allow_public):
    controller(mobile_number, allow_public)

    return {"status": True}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
