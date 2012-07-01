from accounts.models import UserProfile, GalleryImage, ProfileImage, InviteCode, Featured
from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.conf import settings
from sorl.thumbnail import get_thumbnail
import os


def thumbnail(img_path):
    try:
        # try creating a thumbnail
        img = open(os.path.join(settings.MEDIA_ROOT,img_path))
        im = get_thumbnail(img, "300x300")
        return u'<img src="%s" alt="%s" />' % (im.url, img_path)
    except:
        # else link to real image
        absolute_url = os.path.join(settings.MEDIA_URL, image_path)
        return u'<img src="%s" alt="%s" />' % (absolute_url, image_path)


class AdminImageWidget(AdminFileWidget):
    """
    A FileField Widget that displays an image instead of a file path
    if the current file is an image.
    """
    def render(self, name, value, attrs=None):
        output = []
        file_name = str(value)
        if file_name:
            file_path = '%s%s' % (settings.MEDIA_URL, file_name)
            output.append('<a target="_blank" href="%s">%s</a>' % \
                (file_path,thumbnail(file_name)),
            )
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('temporary_profile_url',
                       'profile_image_cropped',
                       'profile_image_uncropped',
                       'user_link',)

    def user_link(self, obj):
        change_url = reverse('admin:auth_user_change', args=(obj.user.id,))
        return mark_safe('<a href="%s">%s</a>' % (change_url, obj.user.email))

    user_link.short_description = 'User'


class FeaturedAdmin(admin.ModelAdmin):
    list_filter = ('city',)


class ImageAdmin(admin.ModelAdmin):
    readonly_fields = ('user_link',)

    def user_link(self, obj):
        change_url = reverse('admin:auth_user_change', args=(obj.user.id,))
        return mark_safe('<a href="%s">%s</a>' % (change_url, obj.user.email))
    user_link.short_description = 'Owner'


    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'file':
            request = kwargs.pop("request", None)
            kwargs['widget'] = AdminImageWidget
            return db_field.formfield(**kwargs)
        sup = super(ImageAdmin, self)
        return sup.formfield_for_dbfield(db_field, **kwargs)



admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(ProfileImage, ImageAdmin)
admin.site.register(GalleryImage, ImageAdmin)
admin.site.register(InviteCode)
admin.site.register(Featured, FeaturedAdmin)
