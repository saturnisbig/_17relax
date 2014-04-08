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
        """ initial with Tag list """
        self.tags = tags

    def fetch(self, today=True):
        result = {}
        if self.tags:
            for t in self.tags:
                result[t.name] = self._fetch_latest_for_tag(t, today)
        return result

    def _fetch_latest_for_tag(self, tag, today):
        """
        fetch the latest news for Tag, return a News list for tag today
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
                if today:
                    news_today = self._today_filter(doc)
                else:
                    news_today = doc
                for d in news_today:
                    docid = d.get('docid', '')
                    if docid:
                        try:
                            News.objects.get(docid=docid)
                        except News.DoesNotExist:
                            result.append(self._insert_latest_news(docid, tag))
            else:
                print 'Fetch news for tag: %s, Error' % tag.name

            return result

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
            news = News()
            doc_json = json.load(resp)
            content = doc_json[doc_json.keys()[0]]
            try:
                title = content['title']
            except KeyError:
                print "Error while Fetching Tag: %s, docid: %s" % (tag.name,
                                                                   docid)
            else:
                if self._filter_test(title):
                    print title
                    news.docid = docid
                    news.tag = tag
                    news.title = title
                    news.comment_num = content['replyCount']
                    news.update_time = content['ptime']
                    img_list = content['img']
                    news.list_pic = img_list[0]['src']
                    news.content, desc = convert_163(content['body'], img_list)
                    news.abstract = desc
                    news.save()
            return news

    def _filter_test(self, title):
        return not (u'测试' in title or 'test' in title)

    def _today_filter(self, doc):
        return [d for d in doc if str(datetime.date.today()) in
                d.get('ptime', '')]


class FetchSohu(object):
    """Fetch latest news for tags of sohu """
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

    def fetch(self, today=True):
        result = {}
        for t in self.tags:
            result[t.name] = self._fetch_latest_for_tag(t, today)
        return result

    def _fetch_latest_for_tag(self, tag, today):
        if tag.tagid > 0:
            return self._fetch_with_tagid(tag, today)
        elif u'搜狐' in tag.come_from:
            return self._fetch_by_search(tag, today)

    def _fetch_by_search(self, tag, today):
        result = []
        url = FetchSohu.search_url % urllib2.quote(tag.name.encode('utf8'))
        try:
            resp = urllib2.urlopen(url)
        except urllib2.URLError, e:
            urllib_error(e)
        else:
            doc = json.load(resp)
            news = [d for d in doc.get('resultList', '')
                    if d.get('newsType', '') == 3]
            if today:
                news_today = self._today_filter(news)
            else:
                news_today = news
            for d in news_today:
                docid = d.get('id', '')
                try:
                    News.objects.get(docid=docid)
                except ObjectDoesNotExist:
                    news = News()
                    news.tag = tag
                    news.docid = docid
                    news.title = d.get('title', '')
                    news.abstract = d.get('abstrac', '')
                    u_time, c_num, content = self._fetch_news(docid)
                    news.update_time = u_time
                    news.comment_num = c_num
                    news.content = content
                    news.save()
                    result.append(news)
        return result

    def _fetch_with_tagid(self, tag, today):
        result = []
        url = FetchSohu.tagid_url % str(tag.tagid)
        try:
            resp = urllib2.urlopen(url)
        except urllib2.URLError, e:
            urllib_error(e)
        else:
            doc = json.load(resp)
            news_list = doc.get('newsList', '')

            if today:
                news_today = self._today_filter(news_list)
            else:
                news_today = news_list

            for d in news_today:
                docid = d.get('newsId', '')
                try:
                    News.objects.get(docid=docid)
                except ObjectDoesNotExist:
                    news = News()
                    news.tag = tag
                    news.docid = docid
                    news.title = d.get('title', '')
                    news.big_pic = d.get('bigPic', '')
                    news.list_pic = d.get('listpic', '')
                    news.abstract = d.get('abstract', '')
                    u_time, c_num, content = self._fetch_news(docid)
                    news.update_time = u_time
                    news.comment_num = c_num
                    news.content = content
                    news.save()
                    result.append(news)
            return result

    def _fetch_news(self, docid):
        url = FetchSohu.detail_url % docid
        try:
            resp = urllib2.urlopen(url)
        except urllib2.URLError as e:
            urllib_error(e)
        else:
            doc_json = json.load(resp)
            if doc_json:
                content = doc_json['content']    # .replace('\\', '')
                if content:
                    content = convert_sohu_img(content)
                return doc_json['time'], int(doc_json['commentNum']), content
            else:
                return ('', 0, '')

    def _today_filter(self, news_list):
        r = [d for d in news_list if datetime.date.today() ==
             datetime.date.fromtimestamp(
                 int(d.get('updateTime', '0000')[:-3]))]
        return r
