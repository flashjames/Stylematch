from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, ListView
from accounts.models import Service
from django.core.urlresolvers import reverse
from braces.views import LoginRequiredMixin

@render_to('display_profile.html')
@login_required
def display_profile(request):
    user_profile = request.user.profile
    url = user_profile.url
    return {'url': url}

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
        self.success_url=reverse('service-new')

    def form_valid(self, form):
        f = form.save(commit=False)
        f.user = self.request.user
        f.save()
        return super(ServiceCreateView, self).form_valid(form)
