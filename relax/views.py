#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import Http404

import json
import urllib2
# Create your views here.
from models import News, Tag
from utils.data_convert import convert_sohu_img, convert_163
from utils.fetch import Fetch163, FetchSohu
from utils.data_import import update_163, update_sohu


def update_today(request):
    tags = Tag.objects.all()
    tags_163 = tags.filter(come_from__contains='网易')
    fetch_163 = Fetch163(tags_163)
    today_163 = fetch_163.fetch()
    tags_sohu = tags.filter(come_from__contains='搜狐')
    fetch_sohu = FetchSohu(tags_sohu)
    today_sohu = fetch_sohu.fetch()
    #print today_163
    return render(request, 'output.html', {'today_163': today_163,
                                           'today_sohu': today_sohu})


def get_tag_news(request, tid):
    tag = Tag.objects.get(id=int(tid))
    if tag:
        news = News.objects.all().filter(tag=tag).order_by('-update_time')
        cn_tag = tag.name
    else:
        news = ['']
        cn_tag = ''

    return render(request, 'article_list.html', {'news': news,
                                                 'cn_tag': cn_tag})


def get_detail_news(request, news_id):
    news = News.objects.get(id=int(news_id))
    if news:
        return render(request, 'article.html', {'article': news})
    else:
        raise Http404


def data_import(request):
    content = ''
    #with open('relax/export-163.txt', 'r') as fh:
    #    for ln, line in enumerate(fh):
    #        line_data = line.split()
    #        if line_data and ln < 2:
    #            #docid = line_data[0]
    #            #docid = '16974926'  #shentucao
    #            #docid = '16778587'  #relaping
    #            #docid = '12672979'  # xianzhidao
    #            article_link = 'http://api.k.sohu.com/api/news/article.go?rt=json&newsId=%s'
    #            #article_link = article_link % docid
    #            #article_link = 'http://c.3g.163.com/nc/article/%s/full.html'
    #            article_link = article_link % line_data[0]
    #            try:
    #                resp = urllib2.urlopen(article_link)
    #            except urllib2.URLError as e:
    #                print 'Error: %s', e.args[0]
    #            else:
    #                doc_json = json.load(resp)
    #                content = doc_json[doc_json.keys()[0]]
    #                body = content['body']
    #                img_list = content['img']
    #                result = convert_163(body, img_list)
    url = 'http://api.k.sohu.com/api/news/article.go?rt=json&newsId=17335522'
    resp = urllib2.urlopen(url)
    doc = json.load(resp)
    content = convert_sohu_img(doc.get('content'))

    return render(request, 'output.html', {'content': content})


def read(request):
    content = News.objects.all()[0]
    return render(request, 'output.html', {'content': content})


def update_tags(request):
    tags_sohu = [{'682': '神吐槽'}, {'683': '热辣评'}, {'681': '鲜知道'},
                 {'0': '狐揭秘'}]
    tags_163 = ['每日轻松一刻', '今日之声', '科技万有瘾力', '科学现场调查']
    for tag in tags_sohu:
        k, v = tag.items()[0]
        try:
            Tag.objects.get(name=v)
        except Tag.DoesNotExist:
            Tag.objects.create(name=v, tagid=int(k), come_from='搜狐网')

    for tag in tags_163:
        try:
            Tag.objects.get(name=tag)
        except Tag.DoesNotExist:
            Tag.objects.create(name=tag, come_from='网易')

    sohu = Tag.objects.all().filter(come_from__contains='搜狐网')
    wangyi = Tag.objects.all().filter(come_from__contains='网易')
    return render(request, 'updated_tags.html', {'tags_sohu': sohu,
                                                 'tags_163': wangyi})


def txt_import(request):
    """ import data from output files """
    update_163()
    #update_sohu()
    news = News.objects.all()
    return render(request, 'updated_sohu.html', {'news': news})
