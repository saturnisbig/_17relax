#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import urllib2
import json
import datetime
import re

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

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
                #print result[t.name]
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
                    #title = u'%s' % d.get('title', '')
                    # the d.get('title') is a unicode string represent by
                    # python str, so use unicode-escape to decode it.
                    title = d.get('title', '')
                    #print type(title)
                    news_title = self._trans_title(title)
                    if docid and title:
                        news_exits = News.objects.filter(
                            Q(docid=docid) | Q(title=news_title)
                        )
                        #print docid, news_title, news_exits
                        if not news_exits:
                            print 'news_exists false', news_exits
                            news = self._insert_latest_news(news_title, docid, tag)
                            import time
                            time.sleep(2)
                            if news:
                                result.append(news)
            else:
                print 'Fetch news for tag: %s, Error' % tag.name

            return result

    def _insert_latest_news(self, news_title, docid, tag):
        """
        add or modify news with docid and tag, return the updated object
        """
        detail_link = Fetch163.detail_link % docid
        try:
            resp = urllib2.urlopen(detail_link)
        except urllib2.URLError as e:
            urllib_error(e)
        else:
            doc_json = json.load(resp)
            content = doc_json[docid]
            try:
                title = content['title']
            except KeyError:
                print "Error while Fetching Tag: %s, docid: %s" % (tag.name,
                                                                   docid)
            else:
                if self._filter_test(title):
                    #print title
                    news = News()
                    news.docid = docid
                    news.tag = tag
                    news.title = news_title
                    news.comment_num = content['replyCount']
                    news.update_time = content['ptime']
                    img_list = content['img']
                    if img_list:
                        news.list_pic = img_list[0]['src']
                    else:
                        news.lict_pic = ''
                    body = content['body']
                    news.content = convert_163(content['body'], img_list)
                    news.abstract = self._retrieve_abstract(body)
                    news.save()
                    return news
            return None

    def _trans_title(self, title):
        print type(title), title
        tables = {
            '（': '(',
            '）': ')',
            '“': '"',
            '”': '"',
            '：': ':'
        }
        for k, v in tables.iteritems():
            title = title.replace(k, v)
        return title

    def _retrieve_abstract(self, content):
        pat = r'</p>'
        content = content.replace('<!--@@PRE-->', '')
        data = re.split(pat, content)  # remove the last item 声明内容
        abstract = ''
        try:
            abstract = data[0].replace('<p>', '').replace('</p>', '')
        except IndexError:
            print data
        return abstract

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
