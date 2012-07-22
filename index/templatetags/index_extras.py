"""
Global filters needed in all templates
"""
import urllib
from django.conf import settings
from django import template
from django.template.base import Node, TemplateSyntaxError, VariableDoesNotExist, resolve_variable
register = template.Library()


# Now, inside a template you can do {{ template_var|pdb }} and enter a pdb session
@register.filter 
def pdb(element):
    import ipdb; ipdb.set_trace()
    return element

@register.simple_tag
def current_url(request, url):
   from django.core.urlresolvers import resolve
   current_url = resolve(request.get_full_path()).url_name
   return current_url


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


@register.filter
def offset(page, limit=10):
    """
    Used to get a tastypie offset value from a page

    Page 1: Offset 0
    Page 2: Offset 5
    Page 3: Offset 10 etc
    """
    return (page - 1) * limit


@register.filter
def repr(level):
    from settings import MESSAGE_TAGS as tags
    return tags.get(level, 'info')


@register.filter
def get_userprofile(user):
    return user.get_profile()


@register.filter
def get_class(self):
    return self.__class__.__name__


@register.filter
def profile_image_thumbnail(userprofile, logged_in_user_profile=False):
    """
    Return a thumbnail to use with sorl.thumbnail
    Example usage in template:

        {% if image|get_class != 'ImageFieldFile' %}
          <img src="{{ image }}">
        {% else %}
        {% thumbnail image 100x100 as im %}
          <img src='{{ im.url }}'>
        {% endthumbnail %}
        {% endif %}

    """

    try:
        # display cropped profile image if there's any
        if userprofile.profile_image_cropped:
            return userprofile.profile_image_cropped.file
        else:
            return userprofile.profile_image_uncropped.file
    except:
        import os
        return os.path.join(settings.STATIC_URL, 'img',
                'default_image_profile_not_logged_in.jpg')


def do_active(parser, token):
    bits = list(token.split_contents())
    if len(bits) < 3:
        raise TemplateSyntaxError, "%r takes at least two arguments" % bits[0]
    return ActiveIfInListNode(bits[1], bits[2:])

def active(parser, token):
    """
    Given an item and an arbitrary number of arguments
    check if any of the items match the first one
    {% active request first second etc %}

    """

    return do_active(parser, token)
active = register.tag(active)

class ActiveIfInListNode(Node):
    def __init__(self, master, comparables):
        self.master, self.comparables = master, comparables

    def __repr__(self):
        return "<ActiveIfInListNode>"

    def render(self, context):
        try:
            request = resolve_variable(self.master, context)
            if not hasattr(request, 'path'):
                return ""
        except VariableDoesNotExist:
            return ""

        comparables = []
        for val in self.comparables:
            try:
                var = resolve_variable(val, context)
            except VariableDoesNotExist:
                var = None
            comparables.append(var)
            
        path = request.path
        # need to urllencode the path, else it wont match swedish-chars
        path = urllib.quote(path.encode('utf-8'))
        if path in comparables:
            return "active"
        return ""
