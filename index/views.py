# Create your views here.
# from django.http import HttpResponse
# from django.shortcuts import render_to_response
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, ListView
from accounts.models import UserProfile

class AboutPageView(TemplateView):
    """
    Display about us page
    """
    template_name = "about_us.html"

class IndexPageView(ListView):
    """
    Display about us page
    """
    context_object_name = "profiles"
    template_name = "index.html"
    queryset = UserProfile.objects.all()
    
    #def get_context_data(self, **kwargs):

def logout_page(request):
    """
    Log users out and re-direct them to the main page.
    """
    auth.logout(request)
    return HttpResponseRedirect('/')
