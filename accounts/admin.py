from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import CustomUser
from accounts.forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_type', 'password1', 'password2'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ("Change Password", {
            'classes': ('change-password-section',),
            "fields": ("password1", "password2")
        }),
        ("Role Info", {"fields": ("user_type",)}),
        ("Permissions", {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ("Important dates", {'fields': ('last_login', 'date_joined')}),
    )

    list_display = BaseUserAdmin.list_display + ("user_type", "is_active")
    list_editable = ("is_active",)

    class Media:
        js = ('accounts/js/custom_user_form.js',)

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs['form'] = self.add_form
        return super().get_form(request, obj, **kwargs)
