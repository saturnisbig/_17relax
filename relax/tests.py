#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase

from models import Article, Tag
# Create your tests here.


class ModelsTest(TestCase):

    def test_could_add_a_tag(self):
        Tag.objects.create(tagid=1, name='每日轻松一刻')
        tag = Tag.objects.all()[0]
        self.assertNotEqual(tag, None)
        print tag.name, type(tag.name)
        self.assertEqual(tag.name, '每日轻松一刻')

    def test_could_add_article(self):
        article = Article()
        docid = '123456'
        article.docid = docid
        article.title = '每日轻松可以'
        article.list_pic = ''
        article.update_time = '2013-03-14 16:00'
        article.content = '这是测试文章内容的'
        article.comment_num = 10
        article.tag = Tag.objects.all()[0]
        article.save()
        article2 = Article.objects.all()[0]
        self.assertEqual(article2.docid, docid)
