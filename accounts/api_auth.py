from tastypie.authorization import Authorization
from tastypie.authentication import BasicAuthentication
from django.contrib.auth.models import User

class PerUserAuthorization(Authorization):
    """
    Only show objects that's related to the user
    http://stackoverflow.com/questions/7015638/django-and-backbone-js-questions
    """
    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            if request.user.is_authenticated():
                object_list = object_list.filter(user=request.user)
                return object_list

            return object_list.none()

class StylistAuthorization(Authorization):
    """
    Only show objects that's related to the user
    http://stackoverflow.com/questions/7015638/django-and-backbone-js-questions
    """
    def apply_limits(self, request, object_list):
        if request and hasattr(request, 'user'):
            if request.user.is_authenticated():

                object_list = object_list.filter(stylist_user=request.user)
                return object_list

        return object_list.none()

class DjangoBasicAuthentication(BasicAuthentication):
    """
    First check session data if user is logged in, with the Django
    authentication.
    If it doesn't find it, fall back to http auth.
    http://stackoverflow.com/questions/7363460
    /how-do-i-check-that-user-already-authenticated-from-tastypie
    """
    def __init__(self, *args, **kwargs):
        super(DjangoBasicAuthentication, self).__init__(*args, **kwargs)

    def is_authenticated(self, request, **kwargs):
        from django.contrib.sessions.models import Session
        if 'sessionid' in request.COOKIES:
            s = Session.objects.get(pk=request.COOKIES['sessionid'])
            if '_auth_user_id' in s.get_decoded():
                u = User.objects.get(id=s.get_decoded()['_auth_user_id'])
                request.user = u
                return True
        return super(DjangoBasicAuthentication, self).is_authenticated(
                                                         request,
                                                         **kwargs)
