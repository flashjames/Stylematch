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
    
class BetaPageView(TemplateView):
    """
    Display beta page
    """
    template_name = "betapage.html"
    
class FeaturesPageView(TemplateView):
    """
    Display features page
    """
    template_name = "features.html"
    
class SignupStep1PageView(TemplateView):
    """
    Display signup step 1 page
    """
    template_name = "signup_step1.html"

class SignupStep2PageView(TemplateView):
    """
    Display signup step 2 page
    """
    template_name = "signup_step2.html"
    

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
