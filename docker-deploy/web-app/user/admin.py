from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import RSSUser
# Register your models here.

class RSSAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_driver',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_driver',)}),
    )


admin.site.register(RSSUser, RSSAdmin)