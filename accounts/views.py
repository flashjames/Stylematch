from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, ListView
from accounts.models import Service
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin
from django.forms import ModelForm
from enhanced_cbv.views import ModelFormSetsView
from enhanced_cbv.views.edit import EnhancedModelFormSet

@render_to('display_profile.html')
@login_required
def display_profile(request):
    user_profile = request.user.profile
    url = user_profile.url
    return {'url': url}


from django.http import HttpResponse
from django.utils import simplejson

class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self,obj='',json_opts={},mimetype="application/json",*args,**kwargs):
        content = simplejson.dumps(obj,**json_opts)
        super(JSONResponse,self).__init__(content,mimetype,*args,**kwargs)

def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"

class ServiceForm(ModelForm):
    class Meta:
        model = Service

class ServiceEnhancedModelFormSet(EnhancedModelFormSet):

    def get_base_formset(self, user, **kwargs):
        """
        Returns the base formset
        """
        # CHANGED: set the queryset to filter services on the user that requested the view
        self.queryset = Service.objects.filter(user__exact=user.id)

        new_kwargs = self.get_kwargs()
        new_kwargs.update(**kwargs)
        return self.get_factory()(**new_kwargs)

    form_class = ServiceForm
    model = Service
    can_order = True
    extra = 1


class ServicesModelView(ModelFormSetsView, LoginRequiredMixin):
    formsets = [ServiceEnhancedModelFormSet]

    template_name = 'authors_articles.html'

    def __init__(self, *args, **kwargs):
        super(ServicesModelView, self).__init__(*args, **kwargs)

        # written here in init since it will give reverse url error
        # if just written in class definition. because urls.py isnt loaded
        # when this class is defined
        self.success_url=reverse('profiles_services')

    def get(self, request, *args, **kwargs):
        self.construct_formsets()
        return self.render_to_response(self.get_context_data())

    def construct_formsets(self):
        """
        Constructs the formsets
        """
        self.formsets_instances = []
        print self.request

        prefixes = {}
        for enhanced_formset in self.enhanced_formsets_instances:

            # CHANGED: added parameter request.user
            base_formset = enhanced_formset.get_base_formset(self.request.user,
                **self.get_factory_kwargs())

            prefix = base_formset.get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1:
                prefix = "%s-%s" % (prefix, prefixes[prefix])

            self.formsets_instances.append(
                base_formset(prefix=prefix, **self.get_formsets_kwargs(
                    enhanced_formset))
            )

class ServiceListView(LoginRequiredMixin, ListView):
    context_object_name = "services"

    def get_queryset(self):
        return Service.objects.filter(user__exact=self.request.user.id)

class ServiceCreateView(LoginRequiredMixin, CreateView):
    model = Service

    def __init__(self, *args, **kwargs):
        super(ServiceCreateView, self).__init__(*args, **kwargs)

        # written here in init since it will give reverse url error
        # if just written in class definition. because urls.py isnt loaded
        # when this class is defined
        self.success_url=reverse('profiles_add_service')

    def form_valid(self, form):
        f = form.save(commit=False)
        f.user = self.request.user
        f.save()
        form.save_m2m()
        return super(ServiceCreateView, self).form_valid(form)

from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
class PerUserAuthorization(Authorization):
    """
    Only show objects that's related to the user
    http://stackoverflow.com/questions/7015638/django-and-backbone-js-questions
    """
    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            if request.user.is_authenticated():
                object_list = object_list.filter(user=request.user)
                return object_list

            return object_list.none()

from tastypie.authentication import BasicAuthentication
from django.contrib.auth.models import User
class DjangoBasicAuthentication(BasicAuthentication):
    """
    First check session data if user is logged in, with the Django authentication.
    If it doesn't find it, fall back to http auth.
    http://stackoverflow.com/questions/7363460
    /how-do-i-check-that-user-already-authenticated-from-tastypie
    """
    def __init__(self, *args, **kwargs):
        super(DjangoBasicAuthentication, self).__init__(*args, **kwargs)

    def is_authenticated(self, request, **kwargs):
        from django.contrib.sessions.models import Session
        if 'sessionid' in request.COOKIES:
            s = Session.objects.get(pk=request.COOKIES['sessionid'])
            if '_auth_user_id' in s.get_decoded():
                u = User.objects.get(id=s.get_decoded()['_auth_user_id'])
                request.user = u
                return True
        return super(DjangoBasicAuthentication, self).is_authenticated(request, **kwargs)

from tastypie.validation import FormValidation
class ServiceResource(ModelResource):

    # TODO: Better way to set user field to current user
    # than having whole function here
    # Possible solution https://github.com/toastdriven/django-tastypie/pull/214
    # but doesnt seem to implemented in our tastypie version
    def obj_create(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        bundle.obj = self._meta.object_class()

        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)

        # CHANGED: Add current user to user field
        bundle.obj.user = request.user
        
        bundle = self.full_hydrate(bundle)
        
        # Save FKs just in case.
        self.save_related(bundle)
        
        # Save the main object.
        bundle.obj.save()

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle
 
    class Meta:
        model = Service
        pass_request_user_to_django = True
        authentication = DjangoBasicAuthentication()
        authorization = PerUserAuthorization()
        queryset = Service.objects.all()
        limit = 50
        max_limit = 0
        validation = FormValidation(form_class=ServiceForm)
