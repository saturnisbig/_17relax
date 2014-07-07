# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Tag.tagid'
        db.alter_column(u'relax_tag', 'tagid', self.gf('django.db.models.fields.CharField')(max_length=80))

    def backwards(self, orm):

        # Changing field 'Tag.tagid'
        db.alter_column(u'relax_tag', 'tagid', self.gf('django.db.models.fields.IntegerField')())

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
            'update_time': ('django.db.models.fields.DateTimeField', [], {'default': "''"}),
            'view_num': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'relax.tag': {
            'Meta': {'object_name': 'Tag'},
            'come_from': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'}),
            'tagid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '80', 'blank': 'True'})
        }
    }

    complete_apps = ['relax']