from django.views.generic import View, TemplateView
from datetime import datetime
from django.http import HttpResponse
from accounts.models import Service
from braces.views import LoginRequiredMixin
import logging

logger = logging.getLogger(__name__)


class StylistBookingView(TemplateView):
    template_name = "stylist_booking.html"

    def get_context_data(self, **kwargs):
        context = super(StylistBookingView, self).get_context_data(**kwargs)
        context['date_today'] = datetime.now().strftime("%Y-%m-%d")
        return context
