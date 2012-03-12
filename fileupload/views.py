from fileupload.models import Picture
from django.views.generic import CreateView, DeleteView

from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

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

class PictureCreateView(CreateView):
    model = Picture
      
    # Add some custom validation to our image field.
    # TODO: Should override a function, earlier in validation flow
    # than form_valid() where it's called right now
    def clean_image(self,image):
        if image:
            if image._size > settings.MAX_IMAGE_SIZE:
                raise ValidationError("Image file too large ( > 20mb )")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")

    def get_form(self, form_class):
        form = super(PictureCreateView, self).get_form(form_class)
        form.instance.user = self.request.user
        #pdb.set_trace()
        return form

    # TODO: should return error in JSONformat, so upload interface
    # can display the error message, and appropriate action for user
    # errors is contained in form._errors
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    
    # Called when we're sure all fields in the form are valid
    def form_valid(self, form):
        
        f = self.request.FILES.get('file')

        # check if image size is ok
        self.clean_image(f)

        filename=get_unique_filename(f.name)
        self.object = form.save(commit=False)
        self.object.save(user=self.request.user,filename=filename)
        
        image_url = self.object.get_image_url()

        data = [{'name': f.name, 'url': image_url, 'thumbnail_url': image_url, 'delete_url': reverse('upload-delete', args=[self.object.id]), 'delete_type': "DELETE"}]

        response = JSONResponse(data, {}, response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

class PictureDeleteView(DeleteView):
    model = Picture

    def delete(self, request, *args, **kwargs):
        """
        This does not actually delete the file, only the database record.
        Implement w
        """
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
