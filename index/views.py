# Create your views here.
# from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, TemplateView
from django.core.urlresolvers import reverse
from accounts.models import UserProfile, GalleryImage
from index.models import BetaEmail
from accounts.api import ProfileResource


class InspirationPageView(ListView):
    """
    TODO:
    Create description of this view
    """
    context_object_name = "pictures"
    template_name = "inspiration.html"
    queryset = GalleryImage.objects.order_by('-upload_date')
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super(InspirationPageView, self).get_context_data(**kwargs)
        return context


class SearchCityView(ListView):
    """
    """
    context_object_name = "profiles"
    template_name = "city_search.html"

    def render_to_response(self, request):
        pr = ProfileResource()
        pr_bundle = pr.build_bundle(request=request)

        import pdb; pdb.set_trace()

        templateview = super(SearchCityView, self).render_to_response(request)

        return templateview

    def get_context_data(self, **kwargs):
        context = super(SearchCityView, self).get_context_data(**kwargs)
        # .title() capitalizes first letter in each word
        context['city'] = self.kwargs['city'].title()
        return context

    def get_queryset(self):
        queryset = UserProfile.objects.filter(visible=True).order_by('?')
        return queryset


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


def error500(request):
    return render_to_response('500.html',
            context_instance=RequestContext(request))
