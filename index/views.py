# coding:utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import auth, messages
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View, ListView, CreateView, TemplateView
from django.core.urlresolvers import reverse
from accounts.models import UserProfile, GalleryImage
from index.models import BetaEmail
from index.forms import TipForm
from accounts.api import ProfileResource
import simplejson as json
from copy import copy
from braces.views import LoginRequiredMixin, StaffRequiredMixin
from cities import *
from django.core.urlresolvers import reverse
from django.shortcuts import redirect


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


def make_pagination_list(list, current):
    def f7(seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if x not in seen and not seen_add(x)]

    if len(list) < 6: return list

    newlist = list[:3] + list[len(list) - 3:]
    newlist += [current - 1, current, current + 1]
    if 0 in newlist:
        newlist.remove(0)
    if current == len(list):
        newlist.remove(current + 1)
    newlist = f7(newlist)
    newlist = sorted(newlist)

    pos = []
    prev = 0
    for idx, page in enumerate(newlist):
        if page > (prev + 1):
            pos.append(idx)
        prev = page

    for i, p in enumerate(pos):
        newlist.insert(p + i, False)

    return newlist


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

        # get a standard profile that is always displayed
        # standard profile is the first profile registered in the city
        try:
            standard_profile = UserProfile.objects.filter(
                                        visible=True,
                                        salon_city__iexact=city)\
                     .order_by('user__date_joined')[0]
        except:
            standard_profile = ""

        # create an artificial request to our API
        json_request = copy(self.request)
        json_request.GET._mutable = True
        json_request.GET['format'] = 'json'

        # set limit and offset
        try:
            offset = int(self.request.GET['offset'])
        except:
            offset = 0

        # execute the request
        resp = self.pr.get_list(json_request,
                                salon_city__iexact=city,
                                profile_image_size="100x100").content

        # get the response
        vals = json.loads(resp)

        if len(vals['objects']) == 0:
            if int(vals['meta']['total_count']) > 0:
                # an invalid offset has been set for the request,
                # repeat the request but with offset = 0
                # this should not happen unless the user explicitly
                # sets the offset
                json_request.GET['offset'] = '0'
                offset = 0
                resp = self.pr.get_list(json_request,
                                        salon_city__iexact=city,
                                        profile_image_size="100x100").content
                vals = json.loads(resp)

        try:
            limit = int(self.request.GET['limit'])
        except:
            limit = self.pr._meta.limit

        # fix pagination
        current_page = offset / limit + 1
        pages = lastpage = vals['meta']['total_count'] / limit + 1
        pages = make_pagination_list(range(1, pages + 1), current_page)
        has_previous = current_page > 1
        has_next = current_page < lastpage
        page_previous = current_page - 1
        page_next = current_page + 1

        # pass additional variables
        if 'offset' in json_request.GET:
            del json_request.GET['offset']
        del json_request.GET['format']
        getvars = ""
        if json_request.GET:
            getvars = "&" + json_request.GET.urlencode()

        # update our context data with the response
        context.update({
            'profiles': vals['objects'],
            'profiles_total': vals['meta']['total_count'],
            'pages': pages,
            'lastpage': lastpage,
            'current_page': current_page,
            'has_previous': has_previous,
            'has_next': has_next,
            'page_previous': page_previous,
            'page_next': page_next,
            'limit': limit,
            'getvars': getvars,
            'standard_profile': standard_profile,
        })
        return context


class BetaEmailView(CreateView):
    """
    Display beta page
    """
    template_name = "betaemailpage.html"
    model = BetaEmail

    def get_success_url(self):
        return reverse('index_page')

    def form_valid(self, form):
        messages.success(self.request, "Din mail är nu registrerad, "
                                       "vi kontaktar dig inom kort!")
        return super(BetaEmailView, self).form_valid(form)


class TipView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    Tip your stylist about us!
    """
    form_class = TipForm
    template_name = "tip.html"

    def get_success_url(self):
        return reverse('index_page')

    def form_valid(self, form):
        messages.success(self.request, "Tack för din anmälan! Vi skickar "
                                       "biobiljetten så fort din frisör"
                                       " skapar sin profil!")
        return super(TipView, self).form_valid(form)


class IndexPageView(TemplateView):
    """
    Display about us page
    """
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexPageView, self).get_context_data(**kwargs)
        context['popular_cities'] = popular
        context['other_cities'] = other
        return context

    def get(self, request):
        # if logged in, redirect to dashboard
        # instead of displaying index poage
        if request.user.is_authenticated():
            return redirect(reverse('dashboard'))
        else:
            return super(IndexPageView, self).get(request)


class LikeView(View):
    """
    An API like view to handle like request via ajax
    """
    def post(self, request, *args, **kwargs):
        id = int(request.POST['id'])
        try:
            image = GalleryImage.objects.get(pk=id)
        except:
            # wrong ID, couldn't find gallery image
            return HttpResponse("The ID is WROOONG")

        voted_images = request.session.get('has_voted', [])
        if id not in voted_images:
            image.votes += 1
            image.save()
            request.session['has_voted'] = voted_images + [id]
        return HttpResponse(str(image.votes))


class StylistView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = "frisor_page.html"


def logout_page(request):
    """
    Log users out and re-direct them to the main page.
    """
    auth.logout(request)
    return HttpResponseRedirect('/')


def error500(request):
    return render_to_response('500.html',
            context_instance=RequestContext(request))
