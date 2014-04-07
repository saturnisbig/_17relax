from django.conf.urls import patterns, include, url


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', '_17relax.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^datain/', 'relax.views.data_import'),
    url(r'^read/', 'relax.views.read'),
    url(r'^updateTags/$', 'relax.views.update_tags'),
    url(r'^updateToday/$', 'relax.views.update_today'),
    url(r'^news/(\d+)/$', 'relax.views.get_detail_news'),
    url(r'^tag/(\d+)/$', 'relax.views.get_tag_news'),
    url(r'^import/$', 'relax.views.txt_import'),

    url(r'^admin/', include(admin.site.urls)),
)
