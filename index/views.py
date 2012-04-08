# Create your views here.
# from django.http import HttpResponse
# from django.shortcuts import render_to_response
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

class AboutPageView(TemplateView):
    """
    Display about us page
    """
    template_name = "about_us.html"

class IndexPageView(TemplateView):
    """
    Display about us page
    """
    template_name = "index.html"

def logout_page(request):
    """
    Log users out and re-direct them to the main page.
    """
    auth.logout(request)
    return HttpResponseRedirect('/')
