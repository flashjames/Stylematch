from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, ListView
from accounts.models import Service
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.http import HttpResponseRedirect
from django.forms import ModelForm

@render_to('display_profile.html')
@login_required
def display_profile(request):
    user_profile = request.user.profile
    url = user_profile.url
    return {'url': url}


from enhanced_cbv.views import ModelFormSetsView


class ServiceForm(ModelForm):
    class Meta:
        model = Service
        exclude = ('user', 'order', 'description', 'display_on_profile', 'price', 'length')


from enhanced_cbv.views.edit import EnhancedFormSet, EnhancedModelFormSet

class ServiceEnhancedModelFormSet(EnhancedModelFormSet):
    queryset = Service.objects.filter(user__exact=1)
    
    def __init__(self, asd, *args, **kwargs):
        print asd
        myvalues = kwargs.pop('hej', "bleh")
        #print it to console (this is a dict by default)
        print myvalues
        #self.request = kwargs.pop('request', None)        
        #queryset = Service.objects.filter(user__exact=1)#self.request.user.id)
        super(ServiceEnhancedModelFormSet, self).__init__(*args, **kwargs)
        
    form_class = ServiceForm
    model = Service
    
    extra = 1

#user_id = None

class ServicesModelView(ModelFormSetsView):

    def get_initial(self):
        """ Passing initial values to the form"""
        # At first initial data should be saved
        super(ServicesModelView, self).get_initial()
        # adding  our values
        print "haj:" + self.request.user
        self.initial= {"myuser": self.request.user}
        return self.initial


    def instantiate_enhanced_formsets(self):
        self.enhanced_formsets_instances = []
        for formset in self.formsets:
            #import pdb;pdb.set_trace()
            print self.request
            enhanced_formset_instance = formset("hi2")
            self.enhanced_formsets_instances.append(enhanced_formset_instance)
        
    def get_formsets_kwargs(self, enhanced_formset):
        print "hi!"
        kwargs = super(ServicesModelView, self).get_formsets_kwargs(
                                                                 enhanced_formset)
        kwargs.update({
            'queryset': enhanced_formset.get_queryset(),
            #'hej': 'test',
            })

        #global user_id = self.request.user.id
        #kwargs.update({
        #    
        #    })

        return kwargs


    #def get(self, request, *args, **kwargs):
    #    #print request
    #    super(ServicesModelView, self).__init__(*args, **kwargs)
    #    return self.render_to_response(self.get_context_data())
                
    formsets = [ServiceEnhancedModelFormSet]
        
    template_name = 'authors_articles.html'
    success_url = '/success/'


ServiceFormSet = modelformset_factory(Service,form=ServiceForm)

class ServiceEditView(CreateView, LoginRequiredMixin):
    template_name = "service_formset.html"
    model = Service
    form_class = ServiceForm
    success_url = 'thanks/'

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            return HttpResponseRedirect('yay/')
        else:
            return HttpResponseRedirect('crap2/')

    def post(self, request):
        #context = self.get_context_data()
        formset = ServiceFormSet(request.POST)
        #formset = context['formset']
 	if formset.is_valid():
            import pdb
            pdb.set_trace()
            pass
            # do something with the cleaned_data on the formsets. 

    #def get_form(self, form_class):
    #    form = super(ServiceEditView,self).get_form(form_class) #instantiate using parent
    #    form.fields['my_list'].queryset = Service.objects.filter(user__exact=self.request.user.id)
    #    return form

    def form_invalid(self, form):
        print form.errors
        return HttpResponseRedirect('crap/')

    def get_context_data(self, **kwargs):
        context = super(ServiceEditView, self).get_context_data(**kwargs)
        
        if self.request.POST:
            context['formset'] = ServiceFormSet(self.request.POST)
        else:
            context['formset'] = ServiceFormSet(queryset=Service.objects.filter(user__exact=self.request.user.id))
        return context

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
