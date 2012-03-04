from fileupload.models import Picture
from django.views.generic import CreateView, DeleteView

from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

from django.conf import settings

import os, uuid
def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"

def get_unique_filename(filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return filename

def get_image_url(filename):
    return os.path.join(settings.STATIC_URL,
                    settings.PATH_USER_IMGS, filename)

class PictureCreateView(CreateView):
    model = Picture
    """
    # Add some custom validation to our image field
    def clean_image(self):
        image = self.cleaned_data.get('image',False)
        if image:
            if image._size > 20*1024*1024:
                raise ValidationError("Image file too large ( > 20mb )")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")
    """
        
    # Called when we're sure all fields in the form are valid
    def form_valid(self, form):
        f = self.request.FILES.get('file')

        # This isnt the most beautiful way to pass user object
        # to the model
        filename=get_unique_filename(f.name)
        self.object = form.save(commit=False)
        self.object.save(user=self.request.user,filename=filename)

        image_url = get_image_url(filename)

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
