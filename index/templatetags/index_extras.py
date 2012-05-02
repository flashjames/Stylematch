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
def google_analytics():
    if not settings.DEBUG:
        return '<script src="%sjs/google_analytics.js" type="text/javascript"></script>' % settings.STATIC_URL

    return ""
