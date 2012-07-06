import json
from django.views.generic.base import TemplateView
from braces.views import LoginRequiredMixin
from statistics.google_analytics import profile_statistics
from accounts.models import UserProfile


class ProfileVisitsView(LoginRequiredMixin, TemplateView):
    template_name = "profile_visits.html"

    def get_context_data(self, **kwargs):
        context = super(ProfileVisitsView, self).get_context_data(**kwargs)
        userprofile = UserProfile.objects.get(user=self.request.user)
        profile_url = userprofile.profile_url
        # since we use the list in a template, to create a javascript array
        # the python list needs to be converted to JSON
        try:
            context['visitor_count_data'] = json.dumps(profile_statistics.get_profile_visits(profile_url))
        # if the google api authentication key is missing
        except AttributeError:
            context['visitor_count_data'] = []
        return context
