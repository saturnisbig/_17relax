#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase

from models import Article, Tag
from utils.fetch import Fetch163, FetchSohu
# Create your tests here.


class ModelsTest(TestCase):
    pass


class Fetch163Test(TestCase):

    def test_could_filter_test_article(self):
        fetch163 = Fetch163(Tag.objects.all().filter(come_from__contains="网易"))
        articles = Article.objects.all()
        tests = articles.filter(title__contains="test")
        ceshi = articles.filter(title__contains="测试")
        print tests
        for d in tests:
            self.assertTrue(fetch163._filter_test(d.title))
        for d in ceshi:
            self.assertTrue(fetch163._filter_test(d.title))


class FetchSohuTest(TestCase):
    pass
