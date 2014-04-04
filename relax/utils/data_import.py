#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import urllib2
import json

from relax.models import News, Tag
from relax.utils.data_convert import convert_163, convert_sohu_img
from relax.utils.basic import urllib_error


def update_163():
    with open('relax/export-163.txt', 'r') as fin:
        for line in fin:
            data = line.split()
            if data:
                try:
                    News.objects.get(docid=data[0])
                except News.DoesNotExist:
                    tag = Tag.objects.all().filter(name__contains=data[1])
                    if not tag:
                        t = Tag.objects.create(name=data[1], come_from='网易')
                        insert_news_163(data, t)
                    else:
                        insert_news_163(data, tag[0])


def insert_news_163(d, t):
    detail_link = 'http://c.3g.163.com/nc/article/%s/full.html'
    detail_link = detail_link % d[0]
    try:
        resp = urllib2.urlopen(detail_link)
    except urllib2.URLError, e:
        with open('relax/updated_fail.txt', 'a') as fout:
            fout.write(' '.join(d))
            urllib_error(e)
    else:
        doc_json = json.load(resp)
        content = doc_json[doc_json.keys()[0]]
        if content:
            title = content['title']
            if not (u'测试' in title or 'test' in title):
                news = News()
                news.tag = t
                news.docid = d[0]
                news.title = content['title']
                news.comment_num = content['replyCount']
                news.update_time = content['ptime']
                img_list = content['img']
                news.content, intro = convert_163(content['body'], img_list)
                news.abstract = intro
                if d[2]:
                    news.list_pic = d[2]
                else:
                    news.list_pic = img_list[0]['src']
                news.save()


def update_sohu():
    with open('relax/export-sohu.txt', 'r') as fin:
        for line in fin:
            data = line.split()
            if data:
                try:
                    News.objects.get(docid=data[0])
                except News.DoesNotExist:
                    tags = Tag.objects.all()
                    if data[1] == '先知道':
                        tag = tags.filter(name__contains='鲜知道')
                    else:
                        tag = tags.filter(name__contains=data[1])

                    if not tag:
                        t = Tag.objects.create(name=data[1], come_from='搜狐网')
                        insert_sohu_news(data, t)
                    else:
                        insert_sohu_news(data, tag[0])


def insert_sohu_news(d, t):
    docid = d[0]
    news_link = 'http://api.k.sohu.com/api/news/article.go?rt=json&newsId=%s'
    news_link = news_link % docid
    print news_link
    try:
        resp = urllib2.urlopen(news_link)
    except urllib2.URLError, e:
        with open('relax/updated_fail.txt', 'a') as fout:
            fout.write('\n'.join(d))
            urllib_error(e)
    else:
        doc_json = json.load(resp)
        news = News()
        news.docid = docid
        news.title = doc_json['title']
        news.abstract = doc_json['shareRead']['description']
        news.list_pic = doc_json['shareRead']['pics']
        news.update_time = doc_json['time']
        news.comment_num = doc_json['commentNum']
        content = doc_json['content']    # .replace('\\', '')
        if content:
            content = convert_sohu_img(content)
        news.content = content
        news.tag = t
        news.save()
