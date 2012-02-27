from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

@render_to('display_profile.html')
@login_required
def display_profile(request):
    user_profile = request.user.profile
    url = user_profile.url
    return {'url': url}
