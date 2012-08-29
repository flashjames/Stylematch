# coding:utf-8
from django.db import models
from django.contrib.auth.models import User
from accounts.models import Service

class CalendarEvent(models.Model):
    start_time = models.DateTimeField("Start tid")
    end_time = models.DateTimeField("Slut tid")
    note = models.CharField("Notering", max_length=200)
    stylist_user = models.ForeignKey(User, editable=False, blank=True, null=True, related_name="+")
    client_user = models.ForeignKey(User, editable=False, blank=True, null=True, related_name="+")
    services = models.ManyToManyField(Service, blank=True)
    def __unicode__(self):
        return str(self.start_time) + " --- " + str(self.end_time)
    
