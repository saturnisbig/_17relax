#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models


class Tag(models.Model):
    name = models.CharField("标签名", max_length=25, unique=True)
    tagid = models.IntegerField("标签ID", blank=True, default=0)
    come_from = models.CharField("来自哪", max_length=25, blank=True)
    ctime = models.DateTimeField(auto_now_add=True)
    #times update daily or weekly

    def __unicode__(self):
        return self.name


class News(models.Model):
    docid = models.CharField("新闻ID", max_length=30, unique=True)
    title = models.CharField("新闻标题", max_length=100)
    big_pic = models.URLField("封面图片", blank=True)
    list_pic = models.URLField("列表显示图片", blank=True)
    abstract = models.CharField("新闻简介", max_length=200, blank=True)
    update_time = models.DateTimeField("新闻更新时间", blank=True, null=True)
    content = models.TextField("新闻内容")
    comment_num = models.IntegerField("新闻评论数", default=0)
    ctime = models.DateTimeField(auto_now_add=True)
    # foreign key must specify 'verbose_name' explicitly.
    tag = models.ForeignKey(Tag, verbose_name="所属标签")
    view_num = models.IntegerField("新闻查看数", default=1)

    def __unicode__(self):
        return self.title
