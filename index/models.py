from django.db import models


class BetaEmail(models.Model):
    email = models.EmailField()

    def __unicode__(self):
        return u'%s' % (self.email)
