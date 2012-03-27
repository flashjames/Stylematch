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

class ServiceForm(ModelForm):
    class Meta:
        model = Service
        exclude = ('user', 'order', 'description', 'display_on_profile', 'price', 'length')

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

    extra = 1


class ServicesModelView(ModelFormSetsView):
    formsets = [ServiceEnhancedModelFormSet]

    template_name = 'authors_articles.html'
    success_url = '/success/'
    
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
