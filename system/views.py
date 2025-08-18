from symbol import subscript

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from account.forms import OrganisationForm, DepartmentFormSet, LocationFormSet
from account.models import Organisation
from system.models import Subscription, Plan, Document, Audit


class HomeView(TemplateView):
    template_name = "admin/home.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            return reverse_lazy('/admin/')
        organisation = Organisation.objects.get(representative=user)
        subscription = Subscription.objects.filter(
            organisation=organisation,
            is_active=True
        )

        if not subscription.exists():
            return redirect(reverse_lazy('packages-view'))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_apps'] = admin.site.get_app_list(self.request)

        documents = Document.objects.all()
        active_audits = Audit.objects.all()


        data = {
            'documents':documents.count(),
            'active_audits':0,
            'due_this':0,
            'capas':0,
            'capa_percentage':0,
            'trained_employees':0,
            'trained_employees_completion':0,
            'employees':0,
            'documents':0,
            'audits':0,
            'capas':0,
            'non_comformance':0,
            'training_records':0,
            'change_control':0,
            'risk_assessment':0,
            'management_review':0,
            'quality_policy':0,
        }
        context.update(data)
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


class PackageView(TemplateView):
    template_name = 'system/packages.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plans = Plan.objects.filter(is_active=True)
        context['plans'] = plans
        return context



class PaymentView(TemplateView):
    template_name = 'system/payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan = self.request.GET.get('plan')
        pq = Plan.objects.get(id=plan)
        context['plan'] = pq
        return context


class PaymentProcessView(View):
    template_name = 'system/payment.html'

    def post(self, request, **kwargs):
        method = request.POST.get("method")
        # Here you'd integrate with payment API
        # For example:
        if method == "mobile_money":
            # validate + send request to MTN / Airtel API
            user = self.request.user
            organisation = Organisation.objects.get(representative=user)
            Subscription.objects.create(
                organisation = organisation,
                plan=Plan.objects.get(pk=1),
                is_active=True
            )
        elif method == "visa":
            # send request to Visa/Mastercard API
            pass

        # Simulate success
        return JsonResponse({
            "success": True,
            "redirect_url": "/"
        })
        # return JsonResponse({"success": False, "message": "Invalid request"})