from django.views.generic import View, TemplateView
from datetime import datetime
from django.http import HttpResponse
from accounts.models import Service

class ClientBookingView(TemplateView):
    template_name = "client_booking.html"

    def get_context_data(self, **kwargs):
        context = super(ClientBookingView, self).get_context_data(**kwargs)
        context['date_today'] = datetime.now().strftime("%Y-%m-%d")
        return context

class BookEventAPI(View):
    """
    An API like view to handle like request via ajax

    """
    def post(self, request, *args, **kwargs):
        #
        service_id = int(request.POST['service_id'])
        try:
            image = Service.objects.get(pk=service_id)
        except:
            # wrong ID, couldn't find service
            return HttpResponse("Couldn't find the ID for this gallery image")
        
        return HttpResponse("booked")

