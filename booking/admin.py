from booking.models import CalendarEvent
from django.contrib import admin

class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time',)
        
admin.site.register(CalendarEvent, CalendarEventAdmin)
