# coding:utf-8
# Create your views here.
# from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, TemplateView
from django.core.urlresolvers import reverse
from accounts.models import UserProfile, GalleryImage, Featured
from index.models import BetaEmail
from accounts.api import ProfileResource
import simplejson as json
from copy import copy


class InspirationPageView(ListView):
    """
    TODO:
    Create description of this view
    """
    context_object_name = "pictures"
    template_name = "inspiration.html"
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super(InspirationPageView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        users = UserProfile.objects.filter(visible=True)
        images = GalleryImage.objects.filter(user__in=[i.pk for i in users],
                                             display_on_profile=True)
        return images.order_by('-upload_date')


class SearchCityView(TemplateView):
    """
    """
    template_name = "city_search.html"
    pr = ProfileResource()

    def get_context_data(self, **kwargs):
        context = super(SearchCityView, self).get_context_data(**kwargs)

        # .title() capitalizes first letter in each word
        city = self.kwargs['city']
        context['city'] = self.kwargs['city'].title()

        # create an artificial request to our API
        json_request = copy(self.request)
        json_request.GET._mutable = True
        json_request.GET['format'] = 'json'

        # execute the request
        resp = self.pr.get_list(json_request,
                                salon_city__iexact=city,
                                profile_image_size="100x100").content

        # get the response
        vals = json.loads(resp)

        # update our context data with the response
        context.update({
            'profiles': vals['objects']
        })
        return context


class BetaEmailView(CreateView):
    """
    Display beta page
    """
    template_name = "betaemailpage.html"
    model = BetaEmail

    def __init__(self, *args, **kwargs):
        super(BetaEmailView, self).__init__(*args, **kwargs)

        # written here in init since it will give reverse url error
        # if just written in class definition. because urls.py isnt loaded
        # when this class is defined
        self.success_url = reverse('beta_index_page')


class IndexPageView(TemplateView):
    """
    Display about us page
    """
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexPageView, self).get_context_data(**kwargs)
        from cities import *
        context['popular_cities'] = popular
        context['other_cities'] = other
        return context


def logout_page(request):
    """
    Log users out and re-direct them to the main page.
    """
    auth.logout(request)
    return HttpResponseRedirect('/')


def error500(request):
    return render_to_response('500.html',
            context_instance=RequestContext(request))
