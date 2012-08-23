from django.utils.functional import SimpleLazyObject

"""
TODO: The queries to database should only be done if the variables are used in a template.
      We should also use one database query to determine both.
"""

def is_stylist(request):
    def is_stylist():
        if hasattr(request, 'user'):
            if request.user.groups.filter(name="Stylist").count():
                return True
        return False
    return {
        'is_stylist': is_stylist,
    }

def is_client(request):
    def is_client():
        if hasattr(request, 'user') and request.user.is_authenticated():
            if request.user.groups.filter(name="Client").count():
                return True
        return False

    return {
        'is_client': is_client,
    }
