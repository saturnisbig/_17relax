#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import urllib2
import json
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from relax.models import Article, Tag
from data_convert import convert_sohu_img, convert_163


class Fetch163(object):
    """ Fetch content from 网易 by tag """
    search_link = 'http://c.3g.163.com/nc/article/search/%s.html'
    detail_link = 'http://c.3g.163.com/nc/article/%s/full.html'

    def __init__(self, tags=''):
        """ initial with Tag object list """
        self.tags = tags

    def fetch(self):
        result = {}
        if self.tags:
            for t in self.tags:
                result[t.name] = self._fetch_latest_for_tag(t)
        return result

    def _fetch_latest_for_tag(self, tag):
        """
        fetch the latest article for Tag object tag
        return a Article obj list for tag today
        """
        result = []
        url = Fetch163.search_link % urllib2.quote(tag.name.encode('utf8'))
        try:
            resp = urllib2.urlopen(url)
        except urllib2.URLError as e:
            print 'update tag: %s with Errors: %s' % (tag, e.args[0])
        else:
            doc = eval(resp.read())
            if doc and type(doc) is list:
                doc_today = [d for d in doc if str(datetime.date.today()) in
                             d.get('ptime', '')]
                for d in doc_today:
                    docid = d.get('docid', '')
                    if docid:
                        result.append(self._insert_latest_article(docid, tag))
                    else:
                        print 'docid not exists: %s' % doc
                return result
            else:
                print 'content not correct: %s' % tag
                return None

    def _insert_latest_article(self, docid, tag):
        """
        add or modify article with docid and tag, return the updated object
        """
        detail_link = Fetch163.detail_link % docid
        try:
            resp = urllib2.urlopen(detail_link)
        except urllib2.URLError as e:
            print 'Fetch docid: %s, but error: %s occurs.' % (docid, e.args[0])
            return None
        else:
            doc_json = json.load(resp)
            content = doc_json[doc_json.keys()[0]]
            if content:
                try:
                    article = Article.objects.get(docid=docid)
                except ObjectDoesNotExist:
                    article = Article()
                    article.docid = docid
                    article.tag = tag
                    article.title = content['title']
                    article.comment_num = content['replyCount']
                    article.update_time = content['ptime']
                    article.content = convert_163(content['body'],
                                                  content['img'])
                    article.save()
                else:
                    print 'article already in db, %s' % article.title
                finally:
                    return article
            else:
                return None


class FetchSohu(object):
    """Fetch latest article for tags of sohu """
    # 鲜知道: subId = 681
    # 热辣评:
    # http://api.k.sohu.com/api/flow/newslist.go?subId=683&pubId=0&sid=9&rt=flowCallback&pageNum=1&pageSize=15&t=1394802872877
    # 神吐槽: subId=682
    # 狐揭秘: should use search
    # 开心一刻: should use search
    search_link = 'http://api.k.sohu.com/api/search/search.go?rt=json&words=%s\
        &pageNo=1'
    article_link = 'http://api.k.sohu.com/api/news/article.go?rt=json&newsId=%s'
    tagid_link = 'http://api.k.sohu.com/api/flow/newslist.go?subId=683&pubId=0\
        &sid=9&pageNum=1&pageSize=15'

    def __init__(self, tags):
        self.tags = tags

    def _fetch_latest_for_tag(self, tag):
        result = []
        if tag.tagid > 0:
            url = FetchSohu.tagid_link % tag.tagid
            try:
                resp = urllib2.urlopen(url)
            except urllib2.URLError as e:
                print 'Error: %s, URL: %s' % (e.args[0], url)
            else:
                articles = eval(resp.read())
                articles = articles.get('newsList', '')
                if articles:
                    today_articles = self._today_filter(articles)
                    for d in today_articles:
                        article = Article()
                        article.tag = tag
                        article.title = d.get('title', '')
                        article.big_pic = d.get('bigPic', '')
                        article.list_pic = d.get('listPic', '')
        else:
            url = FetchSohu.search_link % urllib2.quote(tag.name.encode('utf8'))

    def _today_filter(self, articles):
        r = [d for d in articles if datetime.date.today() ==
             datetime.date.fromtimestamp(int(d.get('updateTime', '0000')[:-3]))]
        return r




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
            content = doc_json['content']    # .replace('\\', '')
            if content:
                content = convert_sohu_img(content)
            article.content = content
            article.tag = t
            article.save()
        except IntegrityError as e2:
            print 'docid: %s, already there. Error: %s' % (docid, e2.args[0])
