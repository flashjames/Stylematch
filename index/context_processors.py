from django.conf import settings # import the settings file

def jquery_script(context):
    return {'JQUERY_SCRIPT': settings.JQUERY_SCRIPT}
