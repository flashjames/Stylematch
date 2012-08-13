# coding:utf-8
from django.db import models

class CalendarEvent(models.Model):
    start_time = models.DateTimeField("Start tid")
    end_time = models.DateTimeField("Slut tid")
    title = models.CharField("Titel på event", max_length=200)
    
