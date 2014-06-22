#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import urllib2, urllib
import json
import datetime

from django.core.exceptions import ObjectDoesNotExist

from relax.models import Tag, News
#from basic import urllib_error


class FetchiFeng(object):
    # id=aid=ORIGIN16917： 频道的文章列表
    # ORIGIN16917: 午FUN来了
    # 16908: 有报天天读
    # 17593: 今日最大声
    type_url = 'http://api.3g.ifeng.com/iosNews?id=aid=ORIGIN%s&type=list&pagesize=20'
    # aid：新闻的id 
    news_url = 'http://api.3g.ifeng.com/ipadtestdoc?aid=%s'

    def __init__(self, tags=[]):
        self.tags = tags

    def update(self):
        result = []
        for tag in self.tags:
            print tag.name
            news_items = self.retrieve_news(FetchiFeng.type_url % tag.tagid)
            for item in news_items:
                if item:
                    try:
                        News.objects.get(docid=item['docid'])
                    except ObjectDoesNotExist:
                        news = News()
                        news.docid = item['docid']
                        news.title = item['title']
                        news.abstract = item['abstract']
                        news.list_pic = item['list_pic']
                        news.comment_num = item['comment_num']
                        news.update_time = item['update_time']
                        news.content = self.fetch_news(item['docid'])
                        news.tag = tag
                        news.save()
                        result.append(news)
                    else:
                        print 'news exists: ', item['title']

        return result
        #self.retrieve_news(FetchiFeng.type_url % '16917')

    def retrieve_news(self, list_url):
        result = []
        try:
            resp = urllib2.urlopen(list_url)
        except urllib2.URLError as e:
            #urllib_error(e)
            print e
        else:
            news_list = json.load(resp)[0].get('body').get('item')
            if news_list:
                d = dict()
                for news in news_list:
                    update_time = self.convert_updateTime(news.get('updateTime'))
                    result.append({'docid':news.get('documentId').split('_')[-1],
                                   'title': news.get('title', ''),
                                   'list_pic': news.get('thumbnail', ''),
                                   'abstract': news.get('introduction', ''),
                                   'update_time': update_time,
                                   'comment_num': news.get('comments', '0'),
                                   })
                    #print (news.get('title', ''), news.get('comments', ''),
                    #       self.convert_updateTime(news.get('updateTime')),
                    #       news.get('thumbnail', ''),
                    #       news.get('documentId').split('_')[-1])
            print result
            return result

    def fetch_news(self, docid=''):
        try:
            resp = urllib2.urlopen(FetchiFeng.news_url % docid)
        except:
            print e
        else:
            data = json.load(resp)
            body = data.get('body')
            return body.get('text', '')

    def convert_updateTime(self, updateTime):
        """convert updateTime to format: 2014-06-21 12:20:20"""
        dt = datetime.datetime.strptime(updateTime, '%Y/%m/%d %H:%M:%S')
        return dt.strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    ifeng = FetchiFeng('tag')
    ifeng.update()
    ifeng.fetch_news()
