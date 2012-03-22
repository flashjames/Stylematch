from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from accounts.models import Service

@render_to('display_profile.html')
@login_required
def display_profile(request):
    user_profile = request.user.profile
    url = user_profile.url
    return {'url': url}

class ServiceCreateView(CreateView):
    model = Service
