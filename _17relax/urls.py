from django.conf.urls import patterns, include, url


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', '_17relax.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^datain/', 'relax.views.data_import'),
    url(r'^read/', 'relax.views.read'),
    url(r'^update-tags/', 'relax.views.update_tags'),
    url(r'^update-sohu/', 'relax.views.update_sohu'),
    url(r'^update-163/', 'relax.views.update_163'),
    url(r'^article/(\d+)/', 'relax.views.get_detail_article'),
    url(r'^tag/(\d+)/', 'relax.views.get_tag_article'),
    url(r'^updateToday/', 'relax.views.update_today'),

    url(r'^admin/', include(admin.site.urls)),
)
