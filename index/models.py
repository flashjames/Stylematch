from django.db import models

# Create your models here.
class BetaEmail(models.Model):
    email = models.EmailField()
    def __unicode__(self):
        return u'%s' % (self.email)

