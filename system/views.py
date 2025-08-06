from django.shortcuts import render
from django.contrib import admin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from account.forms import OrganisationForm, DepartmentFormSet, LocationFormSet


class HomeView(TemplateView):
    template_name = "admin/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_apps'] = admin.site.get_app_list(self.request)
        return context


class RegisterCompany(View):
    template_name = 'system/register_company.html'

    def get(self, *args, **kwargs):
        form = OrganisationForm()
        dept_formset = DepartmentFormSet(prefix='dept')
        loc_formset = LocationFormSet(prefix='loc')
        data = {
        'form': form,
        'dept_formset': dept_formset,
        'loc_formset': loc_formset
    }
        return render(self.request, self.template_name, data)
