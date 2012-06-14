from accounts.models import UserProfile, GalleryImage, ProfileImage, InviteCode
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('temporary_profile_url',
                       'profile_image_cropped',
                       'profile_image_uncropped',
                       'user_link',)

    def user_link(self, obj):
        change_url = reverse('admin:auth_user_change', args=(obj.user.id,))
        return mark_safe('<a href="%s">%s</a>' % (change_url, obj.user.email))

    user_link.short_description = 'User'

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(ProfileImage)
admin.site.register(GalleryImage)
admin.site.register(InviteCode)
