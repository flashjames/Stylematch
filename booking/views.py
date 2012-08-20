from django.views.generic import View, TemplateView
from datetime import datetime
from django.http import HttpResponse
from accounts.models import Service, OpenHours
from braces.views import LoginRequiredMixin
import logging

logger = logging.getLogger(__name__)


class StylistBookingView(TemplateView):
    template_name = "stylist_booking.html"

    def get_context_data(self, **kwargs):
        context = super(StylistBookingView, self).get_context_data(**kwargs)
        context['date_today'] = datetime.now().strftime("%Y-%m-%d")
        openhours_list, openhours_object = OpenHours.objects.get_openinghours(self.request.user)
        context['opening_hours'] = openhours_list
        context['earliest_opening'], context['latest_closing'] = OpenHours.objects.get_max_openingshours(user=self.request.user)
        
        return context
