from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('career_path', 'primary_goal', 'interests', 'experience_level', 'learning_style', 'profile_complete')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_profile_complete')

    def get_profile_complete(self, obj):
        try:
            return obj.profile.profile_complete
        except UserProfile.DoesNotExist:
            return False
    get_profile_complete.short_description = 'Profile Complete'
    get_profile_complete.boolean = True


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'career_path', 'primary_goal', 'experience_level', 'profile_complete', 'created_at')
    list_filter = ('career_path', 'primary_goal', 'experience_level', 'profile_complete')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


# Customize admin site appearance
admin.site.site_header = '🎓 CareerPath Admin'
admin.site.site_title = 'CareerPath Admin Portal'
admin.site.index_title = 'Welcome to CareerPath Administration'
