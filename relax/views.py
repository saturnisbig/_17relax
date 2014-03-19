#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.db import IntegrityError
from django.http import Http404

import json
import urllib2
# Create your views here.
from models import Article, Tag
from utils.data_convert import convert_sohu_img, convert_163


def get_tag_article(request, tid):
    tag = Tag.objects.get(id=int(tid))
    if tag:
        articles = Article.objects.all().filter(tag=tag).order_by('-update_time')
    else:
        articles = ['']

    return render(request, 'article_list.html', {'articles': articles,
                                                 'cn_tag': tag.name})


def update_163(request):
    with open('relax/export-163.txt', 'r') as fin:
        for line in fin:
            data = line.split()
            if data:
                try:
                    Article.objects.get(docid=data[0])
                except Article.DoesNotExist:
                    tag = Tag.objects.all().filter(name__contains=data[1])
                    if not tag:
                        t = Tag.objects.create(name=data[1], come_from='网易')
                        insert_article_163(data, t)
                    else:
                        insert_article_163(data, tag[0])
                else:
                    pass
    articles = Article.objects.all()
    return render(request, 'updated_sohu.html', {'news': articles})


def insert_article_163(d, t):
    detail_link = 'http://c.3g.163.com/nc/article/%s/full.html'
    detail_link = detail_link % d[0]
    try:
        resp = urllib2.urlopen(detail_link)
    except urllib2.URLError as e:
        with open('relax/updated_fail.txt', 'a') as fout:
            fout.write(' '.join(d))
        print 'update article error: %s' % e.args[0]
    else:
        doc_json = json.load(resp)
        content = doc_json[doc_json.keys()[0]]
        if content:
            try:
                article = Article()
                article.tag = t
                article.docid = d[0]
                article.title = content['title']
                article.comment_num = content['replyCount']
                article.update_time = content['ptime']
                article.content = convert_163(content['body'], content['img'])
                article.save()
            except IntegrityError as e2:
                print 'Error while Insert: %s' % e2.args[0]


def get_detail_article(request, article_id):
    article = Article.objects.get(id=int(article_id))
    if article:
        return render(request, 'article.html', {'article': article})
    else:
        raise Http404


def update_sohu(request):
    with open('relax/export-sohu.txt', 'r') as fin:
        for line in fin:
            data = line.split()
            if data and not Article.objects.get(docid=data[0]):
                tag = Tag.objects.all().filter(name__contains=data[1])
                if not tag:
                    t = Tag.objects.create(name=data[1], come_from='搜狐网')
                    insert_article(data, t)
                else:
                    insert_article(data, tag[0])
    articles = Article.objects.all()
    return render(request, 'updated_sohu.html', {'news': articles})


def insert_article(d, t):
    docid = d[0]
    article_link = 'http://api.k.sohu.com/api/news/article.go?rt=json&newsId=%s'
    article_link = article_link % docid
    try:
        resp = urllib2.urlopen(article_link)
    except urllib2.URLError as e:
        with open('relax/updated_fail.txt', 'a') as fout:
            fout.write(' '.join(d))
            print 'update article error: %s' % e.args[0]
    else:
        doc_json = json.load(resp)
        article = Article()
        try:
            article.docid = docid
            article.title = doc_json['title']
            article.abstract = doc_json['shareRead']['description']
            article.big_pic = doc_json['shareRead']['pics']
            article.update_time = doc_json['time']
            article.comment_num = doc_json['commentNum']
            content = doc_json['content']    #.replace('\\', '')
            if content:
                content = convert_sohu_img(content)
            article.content = content
            article.tag = t
            article.save()
        except IntegrityError as e2:
            print 'docid: %s, already there. Error: %s' % (docid, e2.args[0])


def data_import(request):
    content = ''
    with open('relax/export-163.txt', 'r') as fh:
        for ln, line in enumerate(fh):
            line_data = line.split()
            if line_data and ln < 2:
                #docid = line_data[0]
                #docid = '16974926'  #shentucao
                #docid = '16778587'  #relaping
                #docid = '12672979'  # xianzhidao
                #article_link = 'http://api.k.sohu.com/api/news/article.go?rt=json&newsId=%s'
                #article_link = article_link % docid
                article_link = 'http://c.3g.163.com/nc/article/%s/full.html'
                article_link = article_link % line_data[0]
                print line_data[0]
                try:
                    resp = urllib2.urlopen(article_link)
                except urllib2.URLError as e:
                    print 'Error: %s', e.args[0]
                else:
                    doc_json = json.load(resp)
                    content = doc_json[doc_json.keys()[0]]
                    body = content['body']
                    img_list = content['img']
                    result = convert_163(body, img_list)

    return render(request, 'output.html', {'content': result})


def read(request):
    content = Article.objects.all()[0]
    return render(request, 'output.html', {'content': content})


def update_tags(request):
    tags_sohu = [{'682': '神吐槽'}, {'683': '热辣评'}, {'681': '鲜知道'}, '狐揭秘']
    tags_163 = ['每日轻松一刻', '今日之声', '科技万有瘾力']
    try:
        for tag in tags_sohu:
            if tag and type(tag) is dict:
                k, v = tag.items()[0]
                Tag.objects.create(name=v, tagid=k, come_from='搜狐网')
            else:
                Tag.objects.create(name=tag, come_from='搜狐网')

        for tag in tags_163:
            Tag.objects.create(name=tag, come_from='网易')
    except IntegrityError as e:
        print 'Tags already added:%s', e.args[0]

    sohu = Tag.objects.all().filter(come_from__contains='搜狐网')
    wangyi = Tag.objects.all().filter(come_from__contains='网易')
    return render(request, 'updated_tags.html', {'tags_sohu': sohu,
                                                 'tags_163': wangyi})
