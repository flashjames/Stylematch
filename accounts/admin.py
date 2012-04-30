from accounts.models import UserProfile, Picture
from django.contrib import admin


class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields=('temporary_profile_url','display_on_first_page')
    
admin.site.register(UserProfile,UserProfileAdmin)
admin.site.register(Picture)
