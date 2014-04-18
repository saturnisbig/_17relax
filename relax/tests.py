#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from django.test import TestCase
from django.utils.unittest.case import skip

from models import News, Tag
from utils.fetch import Fetch163, FetchSohu
# Create your tests here.


class ModelsTest(TestCase):
    pass


class Fetch163Test(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(name=u"每日轻松一刻", come_from=u"网易")
        self.fetcher = Fetch163(self.tag)

    def test_fetch_latest_for_tag_returns_list_contains_not_none(self):
        news_list = self.fetcher._fetch_latest_for_tag(self.tag, True)
        for item in news_list:
            self.assertIsNotNone(item)

    @skip("already test")
    def test_could_retrieve_news_abstract(self):
        #fetch163 = Fetch163(Tag.objects.all().filter(come_from__contains="网易"))
        news_list = self.fetcher._fetch_latest_for_tag(self.tag, False)
        for news in news_list:
            self.assertNotEqual(0, len(news.abstract))

    def test_could_filter_news_of_today(self):
        news_today = self.fetcher._fetch_latest_for_tag(self.tag, True)[0]
        self.assertIn(str(datetime.date.today()), news_today.update_time)


class FetchSohuTest(TestCase):
    pass
