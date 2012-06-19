"""
Global filters needed in all templates
"""

from django.conf import settings
from django import template
register = template.Library()


# Now, inside a template you can do {{ template_var|pdb }} and enter a pdb session
@register.filter 
def pdb(element):
    import ipdb; ipdb.set_trace()
    return element

@register.simple_tag
def current_url(request):
   from django.core.urlresolvers import resolve
   current_url = resolve(request.get_full_path()).url_name
   return current_url

@register.simple_tag
def active(request, pattern):
    #import pdb;pdb.set_trace()
    import re
    if re.search(pattern, request.path):
        return 'active'
    return ''

@register.simple_tag
def google_analytics():
    if settings.PRODUCTION:
        return '<script src="%sjs/google_analytics.js" type="text/javascript"></script>' % settings.STATIC_URL

    return ""

@register.simple_tag
def intercom_analytics():
    if settings.PRODUCTION:
        return '<script src="%sjs/intercom_analytics.js" type="text/javascript"></script>' % settings.STATIC_URL

    return ""

@register.simple_tag
def facebook():
        return '<script src="%sjs/facebook.js" type="text/javascript"></script>' % settings.STATIC_URL
