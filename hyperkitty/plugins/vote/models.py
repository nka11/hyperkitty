from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

class Rating(models.Model):
    list_address = models.CharField(max_length=255, db_index=True)
    messageid = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(User)
    vote = models.SmallIntegerField()

    def __unicode__(self):
        """Unicode representation"""
        if self.vote == 1:
            return u'%s liked message %s' % (unicode(self.user),
                    unicode(self.messageid))
        else:
            return u'%s disliked message %s' % (unicode(self.user),
                    unicode(self.messageid))

admin.site.register(Rating)
