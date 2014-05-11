# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tag'
        db.create_table(u'relax_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=25)),
            ('tagid', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('come_from', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'relax', ['Tag'])

        # Adding model 'News'
        db.create_table(u'relax_news', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('docid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('big_pic', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('list_pic', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('abstract', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('update_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('comment_num', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['relax.Tag'])),
        ))
        db.send_create_signal(u'relax', ['News'])


    def backwards(self, orm):
        # Deleting model 'Tag'
        db.delete_table(u'relax_tag')

        # Deleting model 'News'
        db.delete_table(u'relax_news')


    models = {
        u'relax.news': {
            'Meta': {'object_name': 'News'},
            'abstract': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'big_pic': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'comment_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'docid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list_pic': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['relax.Tag']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'relax.tag': {
            'Meta': {'object_name': 'Tag'},
            'come_from': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'}),
            'tagid': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        }
    }

    complete_apps = ['relax']