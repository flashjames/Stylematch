from accounts.models import UserProfile, GalleryImage, ProfileImage, InviteCode, Featured, ScheduledCheck
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.conf import settings
from sorl.thumbnail import get_thumbnail
import os

def thumbnail(img):
    try:
        # try creating a thumbnail
        im = get_thumbnail(img, "300x300")
        return u'<img src="%s" />' % (im.url)
    except:
        # else link to real image
        absolute_url = os.path.join(settings.MEDIA_URL, img)
        return u'<img src="%s" />' % (absolute_url)


class AdminImageWidget(AdminFileWidget):
    """
    A FileField Widget that displays an image instead of a file path
    if the current file is an image.
    """
    def render(self, name, value, attrs=None):
        output = []
        try:
            tn = thumbnail(value.file)
        except:
            tn = None
        if tn is not None:
            file_path = '%s%s' % (settings.MEDIA_URL, str(value))
            output.append('<a target="_blank" href="%s">%s</a>' % \
                (file_path,tn),
            )
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


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


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    readonly_fields = ('temporary_profile_url',
                       'profile_image_cropped',
                       'profile_image_uncropped',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        sup = super(UserProfileInline, self)
        formfield = sup.formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'profile_text':
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield


class UserProfileAdmin(UserAdmin):
    inlines = [ UserProfileInline, ]
    list_display = ('username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'userprofile__salon_city',)


admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
admin.site.register(ProfileImage, ImageAdmin)
admin.site.register(GalleryImage, ImageAdmin)
admin.site.register(InviteCode)
admin.site.register(Featured, FeaturedAdmin)
admin.site.register(ScheduledCheck)
