from django import template
from fileupload.models import Picture

register = template.Library()

#@register.tag
def get_gallery_images():
    # TODO: should have limit on number of imgs to display
    user_id=1
    # TODO: should only display gallery images (add type 
    gallery_images = Picture.objects.filter(user=user_id).filter(
        image_type="G")
    print 3*"\n",gallery_images[0].get_image_url(), 3*"\n"
    return {'images': gallery_images}

register.inclusion_tag('fileupload/display_images.html')(get_gallery_images)

@register.filter
def get_image_url(obj):
    return obj.get_image_url()

def get_profile_image():
    return "hej"


