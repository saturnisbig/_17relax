from django.contrib import admin
from relax.models import News, Tag

# Register your models here.
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'tag', 'abstract', 'update_time', 'comment_num',
                    'view_num')
    search_fields = ('title', 'abstract', 'content')
    list_filter = ('update_time', 'tag')
    date_hierarchy = 'update_time'
    ordering = ('-update_time',)
    fields = ('title', 'tag', 'abstract', 'content', 'update_time',
              'comment_num', 'view_num')
    # django ticket 342, but also can't edit at when Add item.
    #readonly_fields = ('tag', 'update_time', 'comment_num')
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['tag', 'update_time', 'comment_num']
        else:
            return []


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'tagid', 'come_from')
    ordering = ('-ctime',)



admin.site.register(News, NewsAdmin)
admin.site.register(Tag, TagAdmin)
