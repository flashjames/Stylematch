import json
from django.views.generic.base import TemplateView
from statistics.google_analytics import profile_statistics


class ProfileVisitsView(TemplateView):
    template_name = "profile_visits.html"

    def get_context_data(self, **kwargs):
        context = super(ProfileVisitsView, self).get_context_data(**kwargs)
        # since we use the list in a template, to create a javascript array
        # the python list needs to be converted to JSON
        #context['data'] = json.dumps(profile_statistics.get_profile_visits())
        return context
