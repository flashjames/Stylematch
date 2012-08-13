from django.views.generic import TemplateView
from datetime import datetime

class ClientBookingView(TemplateView):
    template_name = "client_booking.html"

    def get_context_data(self, **kwargs):
        context = super(ClientBookingView, self).get_context_data(**kwargs)
        context['date_today'] = datetime.now().strftime("%Y-%m-%d")
        return context

