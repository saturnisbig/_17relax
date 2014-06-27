#!/usr/bin/env python
# _*_ coding: utf-8 _*_

from __future__ import absolute_import
from celery import shared_task

from relax.models import Tag
from relax.utils.fetch import Fetch163, FetchSohu
from relax.utils.ifeng_fetch import FetchiFeng

#app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost/')
#app.config_from_object('celeryconfig')

@shared_task
def update():
    tags = Tag.objects.all()
    tags_163 = tags.filter(come_from__contains='网易')
    fetch_163 = Fetch163(tags_163)
    fetch_163.fetch(today=True)
    tags_sohu = tags.filter(come_from__contains='搜狐')
    fetch_sohu = FetchSohu(tags_sohu)
    fetch_sohu.fetch(today=False)
    tags_ifeng = tags.filter(come_from__contains='凤凰网')
    today_ifeng = FetchiFeng(tags_ifeng)
    today_ifeng.update()
