#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import urllib2
import json
import datetime

from django.core.exceptions import ObjectDoesNotExist

from relax.models import News
from data_convert import convert_sohu_img, convert_163
from basic import urllib_error


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
        return a News obj list for tag today
        """
        result = []
        url = Fetch163.search_link % urllib2.quote(tag.name.encode('utf8'))
        try:
            resp = urllib2.urlopen(url)
        except urllib2.URLError as e:
            urllib_error(e)
        else:
            doc = eval(resp.read())
            if doc and type(doc) is list:
                doc_today = doc
                for d in doc_today:
                    docid = d.get('docid', '')
                    if docid:
                        try:
                            News.objects.get(docid=docid)
                        except News.DoesNotExist:
                            result.append(self._insert_latest_news(docid, tag))
                return result
            else:
                print 'content not correct: %s' % tag
                return result

    def _today_filter(self, doc):
        return [d for d in doc if str(datetime.date.today()) in
                d.get('ptime', '')]

    def _insert_latest_news(self, docid, tag):
        """
        add or modify article with docid and tag, return the updated object
        """
        detail_link = Fetch163.detail_link % docid
        try:
            resp = urllib2.urlopen(detail_link)
        except urllib2.URLError as e:
            urllib_error(e)
        else:
            doc_json = json.load(resp)
            content = doc_json[doc_json.keys()[0]]
            if content:
                article = News()
                title = content['title']
                if self._filter_test(title):
                    article.docid = docid
                    article.tag = tag
                    article.title = title
                    article.comment_num = content['replyCount']
                    article.update_time = content['ptime']
                    img_list = content['img']
                    article.list_pic = img_list[0]['src']
                    article.content, intro = convert_163(content['body'],
                                                         img_list)
                    article.abstract = intro
                    article.save()
                return article
            else:
                return None

    def _filter_test(self, title):
        return not (u'测试' in title or 'test' in title)


class FetchSohu(object):
    """Fetch latest article for tags of sohu """
    # 鲜知道: subId = 681
    # 热辣评:
    # http://api.k.sohu.com/api/flow/newslist.go?subId=683&pubId=0&sid=9&
    # rt=flowCallback&pageNum=1&pageSize=15&t=1394802872877
    # 神吐槽: subId=682
    # 狐揭秘: should use search
    # 开心一刻: should use search
    search_url = 'http://api.k.sohu.com/api/search/search.go?rt=json&words=%s'
    detail_url = 'http://api.k.sohu.com/api/news/article.go?rt=json&newsId=%s'
    tagid_url = 'http://api.k.sohu.com/api/flow/newslist.go?subId=%s&pageSize=25'

    def __init__(self, tags):
        self.tags = tags

    def fetch(self):
        result = {}
        for t in self.tags:
            result[t.name] = self._fetch_latest_for_tag(t)
        return result

    def _fetch_latest_for_tag(self, tag):
        if tag.tagid > 0:
            return self._fetch_with_tagid(tag)
        elif u'搜狐' in tag.come_from:
            return self._fetch_by_search(tag)

    def _fetch_by_search(self, tag):
        result = []
        url = FetchSohu.search_url % urllib2.quote(tag.name.encode('utf8'))
        try:
            resp = urllib2.urlopen(url)
        except urllib2.URLError, e:
            urllib_error(e)
        else:
            doc = json.load(resp)
            articles = [d for d in doc.get('resultList', '')
                        if d.get('newsType', '') == 3]
            #today_articles = self._today_filter(articles)
            today_articles = articles
            for d in today_articles:
                docid = d.get('id', '')
                try:
                    News.objects.get(docid=docid)
                except ObjectDoesNotExist:
                    article = News()
                    article.tag = tag
                    article.docid = docid
                    article.title = d.get('title', '')
                    article.abstract = d.get('abstrac', '')
                    u_time, c_num, news = self._fetch_article(docid)
                    article.update_time = u_time
                    article.comment_num = c_num
                    article.content = news
                    article.save()
                    result.append(article)
        return result

    def _fetch_with_tagid(self, tag):
        result = []
        url = FetchSohu.tagid_url % str(tag.tagid)
        try:
            resp = urllib2.urlopen(url)
        except urllib2.URLError, e:
            urllib_error(e)
        else:
            articles = json.load(resp)
            articles = articles.get('newsList', '')
            if articles:
                #today_articles = self._today_filter(articles)
                today_articles = articles
                for d in today_articles:
                    docid = d.get('newsId', '')
                    try:
                        article = News.objects.get(docid=docid)
                    except ObjectDoesNotExist:
                        article = News()
                        article.tag = tag
                        article.docid = docid
                        article.title = d.get('title', '')
                        article.big_pic = d.get('bigPic', '')
                        article.list_pic = d.get('listpic', '')
                        article.abstract = d.get('abstract', '')
                        u_time, c_num, news = self._fetch_article(docid)
                        article.update_time = u_time
                        article.comment_num = c_num
                        article.content = news
                        article.save()
                        result.append(article)
                    else:
                        print 'article already in db, %s' % article.title
                        #article.list_pic = d.get('listpic', '')
                        #article.save()
            return result

    def _fetch_article(self, docid):
        url = FetchSohu.detail_url % docid
        try:
            resp = urllib2.urlopen(url)
        except urllib2.URLError as e:
            urllib_error(e)
            return ('', 0, '')
        else:
            doc_json = json.load(resp)
            if doc_json:
                content = doc_json['content']    # .replace('\\', '')
                if content:
                    content = convert_sohu_img(content)
                return doc_json['time'], int(doc_json['commentNum']), content
            else:
                return ('', 0, '')

    def _today_filter(self, articles):
        r = [d for d in articles if datetime.date.today() ==
             datetime.date.fromtimestamp(int(d.get('updateTime', '0000')[:-3]))]
        print 'filter articles of today: ', r
        return r
