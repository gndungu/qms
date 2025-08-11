from django.apps import apps
from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.contrib.auth import views as auth_views
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.urls import path
from django.shortcuts import render
from account.models import CustomUser, Organisation,  OrganisationLocation, Department,OrganisationStandard


class CustomAdminSite(admin.AdminSite):
    def login(self, request, extra_context=None):
        """
        Displays the login form for the given HttpRequest.
        """
        if request.method == "GET" and not request.user.is_authenticated:
            request.session.set_test_cookie()
        extra_context = extra_context or {}
        extra_context.update({
            'title': _('Log in'),
            'app_path': request.get_full_path(),
            'username_label': _('Email'),
        })
        defaults = {
            'extra_context': extra_context,
            'template_name': 'admin/login.html',
        }
        return auth_views.LoginView.as_view(**defaults)(request)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'



class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm

    fieldsets = (
        (None, {'fields': ('email', 'full_name', 'phone_number', 'password', 'signature', 'role', 'department_head', 'account_type', 'use_two_factor_authentication')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'account_type', 'role', 'use_two_factor_authentication'),
        }),
    )

    list_display = ('email', 'full_name',  'is_staff', 'account_type', 'role', 'department_head', 'use_two_factor_authentication')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email',)
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login')


class OrganisationLocationInline(admin.StackedInline):
    model = OrganisationLocation
    extra = 1


class DepartmentInline(admin.StackedInline):
    model = Department
    extra = 1


class OrganisationStandardInline(admin.StackedInline):
    model = OrganisationStandard
    extra = 1


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'address', 'tin_number', 'region', 'phone', 'sector', 'action_button']
    inlines = [OrganisationLocationInline, DepartmentInline, OrganisationStandardInline]

    def action_button(self, obj):
        url = reverse('customer_detail', args=[obj.pk])  # or your custom URL
        return format_html('<a class="btn btn-block btn-outline-primary" href="{}"><i class="fas fa-book"></i> OPEN</a>', url)

    action_button.short_description = 'Action'
    action_button.allow_tags = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate()  # if needed, for related fields
        return qs

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            cl = response.context_data['cl']
            for result in cl.result_list:
                setattr(result, '_admin_url_id', result.pk)
        except (AttributeError, KeyError):
            pass
        return response



class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'organisation']

# Register your custom user model with the custom admin class
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Department, DepartmentAdmin)