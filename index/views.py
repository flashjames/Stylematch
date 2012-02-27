# Create your views here.
from django.http import HttpResponse
from annoying.decorators import render_to
from django.shortcuts import render_to_response
from django.contrib import auth
from django.http import HttpResponseRedirect

@render_to('index.html')
def index(request):
    return {}

@render_to('profile_index.html')
def profile_index(request):
    return {}


def logout_page(request):
    """
    Log users out and re-direct them to the main page.
    """
    auth.logout(request)
    return HttpResponseRedirect('/')
