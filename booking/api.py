from tastypie.resources import ModelResource
from booking.models import CalendarEvent
import re

# filter on dates - http://stackoverflow.com/questions/1317714/how-can-i-filter-a-date-of-a-datetimefield-in-django
# will need a child of this class for client-booking, with more locked down permissions
# for example we should not send out any information about the event to the client-booking - only
# the start/end-time
class CalendarEventResource(ModelResource):
    def apply_authorization_limits(self, request, object_list):
        # poor mans filtering (objects between dates). according to documentation
        # you should be able to filter client side with get parameters
        # but didnt work.
        if request.GET.has_key("_start_time") and request.GET.has_key("_end_time"):
            start_time = request.GET["_start_time"]
            end_time = request.GET["_end_time"]
            reg_exp = r'\d*\-*'
            if re.match(reg_exp, start_time) and re.match(reg_exp, start_time):                             
                return object_list.filter(start_time__range=[start_time, end_time])

        return object_list
    
    class Meta:
        queryset = CalendarEvent.objects.all()
        resource_name = 'calendar_event'
        # should be sorted after date and maybe return a list for each date
