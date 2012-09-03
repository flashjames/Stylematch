# coding:utf-8
from django.db import models
from django.contrib.auth.models import User
from accounts.models import Service

class CalendarEvent(models.Model):
    TYPE_CHOICES = (
        ('0', 'Ny online bokning'),
        ('1', 'Bekräftad online bokning'),
        ('2', 'Egen tid'),
        ('3', 'Bekräftad telefon bokning'),
        ('4', 'Genomförd klippning'),
        ('5', 'Klienten kom inte')
    )
    event_type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    start_time = models.DateTimeField("Start tid")
    end_time = models.DateTimeField("Slut tid")
    note = models.CharField("Notering", max_length=200)
    stylist_user = models.ForeignKey(User, editable=False, blank=True, null=True, related_name="+")
    client_user = models.ForeignKey(User, editable=False, blank=True, null=True, related_name="+")
    services = models.ManyToManyField(Service, blank=True)
    def __unicode__(self):
        return str(self.start_time) + " --- " + str(self.end_time)
    
