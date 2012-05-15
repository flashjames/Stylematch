# Create your views here.
# from django.http import HttpResponse
# from django.shortcuts import render_to_response
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, ListView, CreateView
from accounts.models import UserProfile
from index.models import BetaEmail

from django.core.urlresolvers import reverse
from django.shortcuts import redirect

class AboutPageView(TemplateView):
    """
    Display about us page
    """
    template_name = "about_us.html"

class ContactPageView(TemplateView):
    """
    Display contact us page
    """
    template_name = "contact_us.html"
    
class BetaPageView(CreateView):
    """
    Display beta page
    """
    template_name = "betapage.html"
    model = BetaEmail

    def __init__(self, *args, **kwargs):
        super(BetaPageView, self).__init__(*args, **kwargs)

        # written here in init since it will give reverse url error
        # if just written in class definition. because urls.py isnt loaded
        # when this class is defined
        self.success_url=reverse('index_page')

    def get(self, request):
        #redirect_to("http://www.google.se", )
        if request.user.is_authenticated():
            return redirect(reverse('profile_display_redirect'))
        else:
            return super(BetaPageView, self).get(request)

    
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

    def get_context_data(self, **kwargs):   
        context = super(IndexPageView, self).get_context_data(**kwargs)
        return context

def logout_page(request):
    """
    Log users out and re-direct them to the main page.
    """
    auth.logout(request)
    return HttpResponseRedirect('/')
