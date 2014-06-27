#!/usr/bin/env python
# _*_ coding: utf-8 _*_

from datetime import timedelta
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'update-every-30-seconds': {
        'task': 'relax.tasks.update',
        'schedule': timedelta(seconds=30),
    },
}

# crontab schedules
#CELERYBEAT_SCHEDULE = {
#    'update-everyday-18pm': {
#        'task': 'relax.tasks.update',
#        'schedule': crontab(hour=18, minute=0),
#    },
#}


CELERY_TIMEZONE = 'Asia/Shanghai'
