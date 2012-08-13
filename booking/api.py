from tastypie.resources import ModelResource
from booking.models import CalendarEvent


# filter on dates - http://stackoverflow.com/questions/1317714/how-can-i-filter-a-date-of-a-datetimefield-in-django
# will need a child of this class for client-booking, with more locked down permissions
# for example we should not send out any information about the event to the client-booking - only
# the start/end-time
class CalendarEventResource(ModelResource):
    #def apply_authorization_limits(self, request, object_list):
    #import pdb;pdb.set_trace()
    #return object_list.filter(start_time__range=["2012-01-01","2012-08-10"])
    
    class Meta:
        queryset = CalendarEvent.objects.all()
        resource_name = 'calendar_event'
        # should be sorted after date and maybe return a list for each date
