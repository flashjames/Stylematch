from fileupload.models import Picture
from django.views.generic import CreateView, DeleteView

from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django import forms
from braces.views import LoginRequiredMixin

from django.conf import settings

import os, uuid, pdb

def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"

def get_unique_filename(filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return filename

def convert_bytes(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2iT' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2iG' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.1fMB' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.iKB' % kilobytes
    else:
        size = '%.iB' % bytes
    return size

class PictureForm(forms.ModelForm):
    def clean_file(self):
        file = self.cleaned_data['file']
        if file:
            if file._size > settings.MAX_IMAGE_SIZE:
                raise ValidationError("Image file too large ( > %s )" % convert_bytes(settings.MAX_IMAGE_SIZE))
            return file
        else:
            raise ValidationError("Couldn't read uploaded image")

    class Meta:
        model = Picture

class PictureCreateView(LoginRequiredMixin, CreateView):
    model = Picture
    form_class = PictureForm
      
    def get_form(self, form_class):
        form = super(PictureCreateView, self).get_form(form_class)
        form.instance.user = self.request.user
        return form

    def form_invalid(self, form):
        data = [{
            # all form errors to a string, use list comprehension since every error
            # is a ErrorList object, and remove the "*" from error string with [1:]
            'error': "".join([ (error.as_text())[1:] for error in form.errors.values()]),
            }]
        response = JSONResponse(data, {}, response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
    
    # Called when we're sure all fields in the form are valid
    def form_valid(self, form):
        
        f = self.request.FILES.get('file')

        filename=get_unique_filename(f.name)

        # add data to form fields that will be saved to db
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.filename = filename
        # default image type for now, Gallery
        self.object.image_type = 'G'
        self.object.save()

        image_url = self.object.get_image_url()

        data = [{'name': f.name, 'url': image_url, 'thumbnail_url': image_url, 'delete_url': reverse('upload-delete', args=[self.object.id]), 'delete_type': "DELETE"}]

        response = JSONResponse(data, {}, response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

class PictureDeleteView(LoginRequiredMixin, DeleteView):
    model = Picture

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        response = JSONResponse(True, {}, response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self,obj='',json_opts={},mimetype="application/json",*args,**kwargs):
        content = simplejson.dumps(obj,**json_opts)
        super(JSONResponse,self).__init__(content,mimetype,*args,**kwargs)
