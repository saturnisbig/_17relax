from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=25, unique=True)
    tagid = models.IntegerField(blank=True, default=0)
    come_from = models.CharField(max_length=25, blank=True)
    ctime = models.DateTimeField(auto_now_add=True)
    #times update daily or weekly

    def __unicode__(self):
        return self.name


class Article(models.Model):
    docid = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=100)
    big_pic = models.URLField(blank=True)
    list_pic = models.URLField(blank=True)
    abstract = models.CharField(max_length=200, blank=True)
    update_time = models.DateTimeField()
    content = models.TextField()
    comment_num = models.IntegerField(default=0)
    ctime = models.DateTimeField(auto_now_add=True)
    tag = models.ForeignKey(Tag)

    def __unicode__(self):
        return self.title
