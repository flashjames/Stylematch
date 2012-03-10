from django import template
from fileupload.models import Picture

register = template.Library()

"""
Template functions to display user uploaded images
"""

def get_images(user, image_type):
    try:
        # make sure template have inputed a valid user object
        user_id = user.id
    except AttributeError:
        msg = "You need to input a valid User object"
        raise template.TemplateSyntaxError(msg)

    # TODO: should have limit on number of imgs to display
    images = Picture.objects.filter(user=user_id).filter(
        image_type=image_type)

    return images

@register.inclusion_tag('fileupload/display_images.html')
def get_gallery_images(user, limit=0):
    # 'G' = gallery images
    gallery_images = get_images(user, 'G')
    return {'css_class': 'gallery-image','images': gallery_images}

@register.filter
def get_image_url(obj):
    return obj.get_image_url()

@register.inclusion_tag('fileupload/display_images.html')
def get_profile_image(user):
    # 'C' = current profile image
    profile_image = get_images(user, 'C')
    return {'css_class': 'profile-image','images': profile_image}


