from accounts.models import UserProfile, GalleryImage, ProfileImage, InviteCode
from django.contrib import admin


class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('temporary_profile_url',
                       'profile_image_cropped',
                       'profile_image_uncropped',)

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(ProfileImage)
admin.site.register(GalleryImage)
admin.site.register(InviteCode)
