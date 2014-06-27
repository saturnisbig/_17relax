#!/usr/bin/env python
# _*_ coding: utf-8 _*_

from __future__ import absolute_import
import os
#from datetime import timedelta
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '_17relax.settings')

app = Celery('_17relax', backend='amqp', broker='amqp://guest@localhost/')
app.config_from_object('django.conf:settings')

app.conf.CELERYBEAT_SCHEDULE = {
    'update-every-30-seconds': {
        'task': 'relax.tasks.update',
        'schedule': crontab(hour=23, minute=30),
    },
}

#app.config_from_object('celeryconfig')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
