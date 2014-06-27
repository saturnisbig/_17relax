#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import json
import urllib2
# Create your views here.
from models import News, Tag
from utils.data_convert import convert_sohu_img, convert_163
from utils.fetch import Fetch163, FetchSohu
from relax.utils.ifeng_fetch import FetchiFeng


def comment_view(request):
    return render(request, 'comment_list.html')


def home(request):
    news = News.objects.all()

    #today = str(datetime.date.today())
    #news_today = news.filter(update_time__contains=today)
    page = request.GET.get('p', 1)
    news_today = news.order_by('-update_time')
    paginator = Paginator(news_today, 10)
    page = int(page)
    try:
        news_today = paginator.page(page)
    except PageNotAnInteger:
        news_today = paginator.page(1)
    except EmptyPage:
        news_today = paginator.page(paginator.num_pages)

    relax_tag = Tag.objects.get(id=5)
    relax_news = news.filter(tag=relax_tag).order_by('-update_time')[:2]

    voice_tag = Tag.objects.get(id=6)
    voice_news = news.filter(tag=voice_tag).order_by('-update_time')[:2]

    tucao_tag = Tag.objects.get(id=1)
    tucao_news = news.filter(tag=tucao_tag).order_by('-update_time')[:2]

    laping_tag = Tag.objects.get(id=2)
    laping_news = news.filter(tag=laping_tag).order_by('-update_time')[:2]

    return render(request, 'home.html', {
        'news': news_today,
        'relax_news': relax_news,
        'voice_news': voice_news,
        'tucao_news': tucao_news,
        'laping_news': laping_news
    })


def update_today(request):
    tags = Tag.objects.all()
    tags_163 = tags.filter(come_from__contains='网易')
    fetch_163 = Fetch163(tags_163)
    today_163 = fetch_163.fetch(today=True)
    tags_sohu = tags.filter(come_from__contains='搜狐')
    fetch_sohu = FetchSohu(tags_sohu)
    today_sohu = fetch_sohu.fetch(today=False)
    tags_ifeng = tags.filter(come_from__contains='凤凰网')
    today_ifeng = FetchiFeng(tags_ifeng)
    today_ifeng.update()
    #print today_163
    return render(request, 'output.html', {'today_163': today_163,
                                           'today_sohu': today_sohu})


def get_tag_news(request, tid):
    try:
        tag = Tag.objects.get(id=int(tid))
    except Tag.DoesNotExist:
        news = ['']
    else:
        ordered_news = tag.news_set.order_by('-update_time')
        page = request.GET.get('p', 1)
        paginator = Paginator(ordered_news, 10)
        page = int(page)
        try:
            news = paginator.page(page)
        except PageNotAnInteger:
            news = paginator.page(1)
        except EmptyPage:
            news = paginator.page(paginator.num_pages)

    return render(request, 'news_list.html', {'news': news,
                                                 'tag': tag})


def get_detail_news(request, news_id):
    news = News.objects.get(id=int(news_id))
    if news:
        news.view_num += 1
        news.save()
        return render(request, 'news.html', {'article': news})
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
    #update_163()
    #update_sohu()
    news = News.objects.all()
    return render(request, 'updated_sohu.html', {'news': news})
